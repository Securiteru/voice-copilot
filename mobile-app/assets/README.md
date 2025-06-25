# Assets Directory

This directory contains the app icons and images for the Voice Copilot mobile app.

## Required Files

For a complete Expo app, you need these files:

- `icon.png` - App icon (1024x1024 px)
- `adaptive-icon.png` - Android adaptive icon (1024x1024 px)
- `splash.png` - Splash screen image (1284x2778 px for iPhone 12)
- `favicon.png` - Web favicon (48x48 px)

## Generating Assets

You can use Expo's asset generation tools:

```bash
# Install the asset generator
npm install -g @expo/image-utils

# Generate all assets from a single 1024x1024 icon
npx expo install expo-asset-utils
```

Or create them manually using any image editor.

## Placeholder Assets

For development, you can use simple colored squares:

- **icon.png**: 1024x1024 blue square with microphone symbol
- **adaptive-icon.png**: Same as icon.png
- **splash.png**: 1284x2778 white background with app name
- **favicon.png**: 48x48 version of the icon

## Design Guidelines

### App Icon
- Use a microphone or voice wave symbol
- Keep it simple and recognizable at small sizes
- Use the app's primary colors (blue/purple theme)
- Ensure good contrast

### Splash Screen
- Keep it minimal
- Show app name and/or logo
- Use consistent branding
- Fast loading is more important than complex graphics

## Current Status

This directory currently contains placeholder files. Replace them with proper assets before building for production.