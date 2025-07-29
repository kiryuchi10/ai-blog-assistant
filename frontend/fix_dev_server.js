const fs = require('fs');
const path = require('path');

// Fix for the Dev Server allowedHosts issue
const webpackConfigPath = path.join(__dirname, 'node_modules', 'react-scripts', 'config', 'webpackDevServer.config.js');

if (fs.existsSync(webpackConfigPath)) {
    let config = fs.readFileSync(webpackConfigPath, 'utf8');
    
    // Fix the allowedHosts issue
    config = config.replace(
        /allowedHosts:\s*\[\s*\]/g,
        'allowedHosts: ["localhost", ".localhost", "127.0.0.1", ".127.0.0.1"]'
    );
    
    fs.writeFileSync(webpackConfigPath, config);
    console.log('✅ Fixed webpack dev server configuration');
} else {
    console.log('⚠️  Webpack config file not found, creating alternative solution...');
    
    // Create a custom start script
    const startScript = `
const { spawn } = require('child_process');

// Set environment variables to fix the dev server
process.env.DANGEROUSLY_DISABLE_HOST_CHECK = 'true';
process.env.SKIP_PREFLIGHT_CHECK = 'true';

// Start the development server
const child = spawn('npx', ['react-scripts', 'start'], {
    stdio: 'inherit',
    shell: true,
    env: {
        ...process.env,
        DANGEROUSLY_DISABLE_HOST_CHECK: 'true',
        SKIP_PREFLIGHT_CHECK: 'true'
    }
});

child.on('error', (error) => {
    console.error('Failed to start dev server:', error);
});
`;
    
    fs.writeFileSync(path.join(__dirname, 'start-dev.js'), startScript);
    console.log('✅ Created alternative start script: start-dev.js');
    console.log('   Run with: node start-dev.js');
}