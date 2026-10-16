import {Config} from '@remotion/cli/config';

// Use this machine's installed Chrome; override on another machine if needed.
Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe');
Config.setCodec('h264');
Config.setCrf(18);
Config.setPixelFormat('yuv420p');
