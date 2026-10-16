import {Config} from '@remotion/cli/config';
Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE || '/usr/bin/google-chrome');
Config.setCodec('h264'); // CRF is passed per command (wav/audio renders reject --crf)
Config.setOverwriteOutput(true);
