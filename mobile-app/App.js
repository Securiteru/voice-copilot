import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Alert, Dimensions, ScrollView } from 'react-native';
import { 
  Provider as PaperProvider, 
  DefaultTheme,
  Button,
  Card,
  Title,
  Paragraph,
  TextInput,
  Chip,
  ActivityIndicator,
  Snackbar,
  IconButton,
  Text
} from 'react-native-paper';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { StatusBar } from 'expo-status-bar';

const { width, height } = Dimensions.get('window');

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#6200ee',
    accent: '#03dac4',
  },
};

export default function App() {
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const [serverUrl, setServerUrl] = useState('http://192.168.1.100:8000');
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordingTimer, setRecordingTimer] = useState(null);

  useEffect(() => {
    checkServerConnection();
    setupAudio();
    
    return () => {
      if (recordingTimer) {
        clearInterval(recordingTimer);
      }
    };
  }, []);

  const setupAudio = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
    } catch (error) {
      console.error('Failed to setup audio:', error);
      showSnackbar('Failed to setup audio permissions');
    }
  };

  const checkServerConnection = async () => {
    try {
      const response = await fetch(`${serverUrl}/health`, {
        method: 'GET',
        timeout: 5000,
      });
      
      if (response.ok) {
        setConnectionStatus('connected');
        showSnackbar('Connected to server');
      } else {
        setConnectionStatus('error');
        showSnackbar('Server responded with error');
      }
    } catch (error) {
      console.error('Connection check failed:', error);
      setConnectionStatus('disconnected');
      showSnackbar('Cannot connect to server');
    }
  };

  const showSnackbar = (message) => {
    setSnackbarMessage(message);
    setSnackbarVisible(true);
  };

  const startRecording = async () => {
    try {
      if (connectionStatus !== 'connected') {
        showSnackbar('Please connect to server first');
        return;
      }

      console.log('Starting recording...');
      
      const { recording } = await Audio.Recording.createAsync({
        android: {
          extension: '.wav',
          outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_DEFAULT,
          audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_DEFAULT,
          sampleRate: 16000,
          numberOfChannels: 1,
          bitRate: 128000,
        },
        ios: {
          extension: '.wav',
          outputFormat: Audio.RECORDING_OPTION_IOS_OUTPUT_FORMAT_LINEARPCM,
          audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
          sampleRate: 16000,
          numberOfChannels: 1,
          bitRate: 128000,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
      });

      setRecording(recording);
      setIsRecording(true);
      setRecordingDuration(0);
      
      // Start timer
      const timer = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
      setRecordingTimer(timer);
      
      console.log('Recording started');
      showSnackbar('Recording started - hold the button');
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      showSnackbar('Failed to start recording');
    }
  };

  const stopRecording = async () => {
    try {
      if (!recording) return;

      console.log('Stopping recording...');
      setIsRecording(false);
      
      // Clear timer
      if (recordingTimer) {
        clearInterval(recordingTimer);
        setRecordingTimer(null);
      }
      
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      
      if (uri) {
        console.log('Recording saved to:', uri);
        await uploadAndTranscribe(uri);
      }
      
    } catch (error) {
      console.error('Failed to stop recording:', error);
      showSnackbar('Failed to stop recording');
    }
  };

  const uploadAndTranscribe = async (audioUri) => {
    try {
      setIsProcessing(true);
      showSnackbar('Processing audio...');
      
      // Create form data
      const formData = new FormData();
      formData.append('audio', {
        uri: audioUri,
        type: 'audio/wav',
        name: 'recording.wav',
      });

      console.log('Uploading to:', `${serverUrl}/transcribe`);
      
      const response = await fetch(`${serverUrl}/transcribe`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = await response.json();
      
      if (result.success && result.text) {
        setTranscribedText(result.text);
        showSnackbar(`Transcribed in ${result.transcription_time?.toFixed(2)}s`);
      } else {
        showSnackbar(result.error || 'Transcription failed');
      }
      
    } catch (error) {
      console.error('Upload failed:', error);
      showSnackbar('Failed to upload audio');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getConnectionColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#4caf50';
      case 'error': return '#ff9800';
      case 'disconnected': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  return (
    <PaperProvider theme={theme}>
      <View style={styles.container}>
        <StatusBar style="auto" />
        
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Header */}
          <Card style={styles.headerCard}>
            <Card.Content>
              <Title style={styles.title}>Voice Copilot</Title>
              <View style={styles.connectionRow}>
                <Chip 
                  icon="circle" 
                  style={[styles.statusChip, { backgroundColor: getConnectionColor() }]}
                  textStyle={{ color: 'white' }}
                >
                  {connectionStatus}
                </Chip>
                <IconButton
                  icon="refresh"
                  size={20}
                  onPress={checkServerConnection}
                />
              </View>
            </Card.Content>
          </Card>

          {/* Server Configuration */}
          <Card style={styles.configCard}>
            <Card.Content>
              <TextInput
                label="Server URL"
                value={serverUrl}
                onChangeText={setServerUrl}
                mode="outlined"
                placeholder="http://192.168.1.100:8000"
                style={styles.serverInput}
              />
              <Button 
                mode="outlined" 
                onPress={checkServerConnection}
                style={styles.testButton}
              >
                Test Connection
              </Button>
            </Card.Content>
          </Card>

          {/* Recording Section */}
          <Card style={styles.recordingCard}>
            <Card.Content style={styles.recordingContent}>
              {isRecording && (
                <View style={styles.recordingInfo}>
                  <Text style={styles.recordingText}>Recording...</Text>
                  <Text style={styles.durationText}>{formatDuration(recordingDuration)}</Text>
                </View>
              )}
              
              {isProcessing && (
                <View style={styles.processingInfo}>
                  <ActivityIndicator size="large" color={theme.colors.primary} />
                  <Text style={styles.processingText}>Processing audio...</Text>
                </View>
              )}
              
              <Button
                mode="contained"
                onPress={isRecording ? stopRecording : startRecording}
                disabled={isProcessing || connectionStatus !== 'connected'}
                style={[
                  styles.recordButton,
                  isRecording && styles.recordingButton
                ]}
                contentStyle={styles.recordButtonContent}
                labelStyle={styles.recordButtonLabel}
                icon={isRecording ? "stop" : "microphone"}
              >
                {isRecording ? "Stop Recording" : "Hold to Record"}
              </Button>
              
              <Text style={styles.instructionText}>
                {connectionStatus === 'connected' 
                  ? "Tap and hold the button while speaking"
                  : "Connect to server first"
                }
              </Text>
            </Card.Content>
          </Card>

          {/* Transcription Result */}
          {transcribedText ? (
            <Card style={styles.resultCard}>
              <Card.Content>
                <Title>Transcription</Title>
                <Paragraph style={styles.transcribedText}>
                  {transcribedText}
                </Paragraph>
                <Button
                  mode="outlined"
                  onPress={() => setTranscribedText('')}
                  style={styles.clearButton}
                >
                  Clear
                </Button>
              </Card.Content>
            </Card>
          ) : null}
        </ScrollView>

        <Snackbar
          visible={snackbarVisible}
          onDismiss={() => setSnackbarVisible(false)}
          duration={3000}
        >
          {snackbarMessage}
        </Snackbar>
      </View>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  headerCard: {
    marginBottom: 16,
  },
  title: {
    textAlign: 'center',
    fontSize: 28,
    fontWeight: 'bold',
  },
  connectionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  statusChip: {
    marginRight: 8,
  },
  configCard: {
    marginBottom: 16,
  },
  serverInput: {
    marginBottom: 12,
  },
  testButton: {
    marginTop: 8,
  },
  recordingCard: {
    marginBottom: 16,
    minHeight: 200,
  },
  recordingContent: {
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 160,
  },
  recordingInfo: {
    alignItems: 'center',
    marginBottom: 20,
  },
  recordingText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#f44336',
  },
  durationText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#f44336',
    marginTop: 4,
  },
  processingInfo: {
    alignItems: 'center',
    marginBottom: 20,
  },
  processingText: {
    fontSize: 16,
    marginTop: 12,
    color: '#666',
  },
  recordButton: {
    width: width * 0.7,
    marginBottom: 16,
  },
  recordingButton: {
    backgroundColor: '#f44336',
  },
  recordButtonContent: {
    height: 60,
  },
  recordButtonLabel: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  instructionText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 14,
  },
  resultCard: {
    marginBottom: 16,
  },
  transcribedText: {
    fontSize: 16,
    lineHeight: 24,
    marginVertical: 12,
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  clearButton: {
    marginTop: 8,
  },
});