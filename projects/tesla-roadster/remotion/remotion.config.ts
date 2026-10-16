import {Config} from '@remotion/cli/config';
Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE || '/usr/bin/google-chrome');
Config.setCodec('h264');
Config.setCrf(18);
Config.setPixelFormat('yuv420p');
Config.setOverwriteOutput(true);
