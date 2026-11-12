## Credits & Acknowledgements

This project builds upon the original [ss14-tts-api](https://github.com/Rxup/ss14-tts-api) by **Rxup**, which provided the initial API foundation and inspiration for this implementation.

Since then, the project has undergone substantial development and adaptation for VanGuard SS14, including:

- Migration from Silero v3 to Silero V5 CIS Base.
- Removal of StressRNN in favor of model-native processing.
- Advanced FFmpeg audio processing, including `dynaudnorm` and `alimiter`.
- An automated CI/CD pipeline with Pytest-based testing.
- Native systemd deployment, without requiring Docker.

We sincerely thank **Rxup** for the original project, its ideas, and the foundational work that made this development possible.