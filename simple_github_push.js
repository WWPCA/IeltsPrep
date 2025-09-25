import { Octokit } from '@octokit/rest'
import { readFileSync, readdirSync, statSync } from 'fs'
import { join, relative } from 'path'

let connectionSettings;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found for repl/depl');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=github',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;

  if (!connectionSettings || !accessToken) {
    throw new Error('GitHub not connected');
  }
  return accessToken;
}

async function getUncachableGitHubClient() {
  const accessToken = await getAccessToken();
  return new Octokit({ auth: accessToken });
}

// Function to get all files excluding some large files that might cause issues
function getAllFiles(dirPath, arrayOfFiles = []) {
  const files = readdirSync(dirPath)
  const skipFiles = ['.DS_Store', 'Thumbs.db', '.git'];
  
  files.forEach(function(file) {
    if (skipFiles.includes(file)) return;
    
    const fullPath = join(dirPath, file)
    if (statSync(fullPath).isDirectory()) {
      arrayOfFiles = getAllFiles(fullPath, arrayOfFiles)
    } else {
      // Skip very large files that might cause issues
      const stats = statSync(fullPath);
      if (stats.size < 100 * 1024 * 1024) { // Skip files larger than 100MB
        arrayOfFiles.push(fullPath)
      }
    }
  })

  return arrayOfFiles
}

async function uploadFileToGitHub(octokit, owner, repo, filePath, content, isBase64 = false) {
  try {
    const { data } = await octokit.rest.repos.createOrUpdateFileContents({
      owner,
      repo,
      path: filePath,
      message: `Add ${filePath}`,
      content: isBase64 ? content : Buffer.from(content).toString('base64'),
      branch: 'main'
    });
    return { success: true, sha: data.content.sha };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function pushToGitHub() {
  try {
    const octokit = await getUncachableGitHubClient();
    
    const owner = 'WWPCA';
    const repo = 'Templates';
    const sourcePath = './website_ui_package';
    
    console.log('Starting GitHub push using contents API...');

    // First, create a README.md to initialize the repository
    const readmeContent = `# IELTS GenAI Prep - Complete Website UI Package

This repository contains the complete website UI package for the IELTS GenAI Prep platform.

## Features

- **97+ HTML Templates**: Complete page structure
- **Professional Design**: Purple gradient theme with responsive layout
- **Flask Application**: Full backend with all routes
- **Static Assets**: CSS, JavaScript, images, and icons
- **SEO Optimized**: robots.txt and sitemap.xml included
- **Mobile Responsive**: Mobile-first design approach

## Quick Start

1. Clone this repository
2. Install dependencies: \`pip install -r requirements.txt\`
3. Run the application: \`python app.py\`
4. Open http://localhost:5000 in your browser

## Structure

- \`templates/\` - HTML templates (97+ files)
- \`static/\` - CSS, JavaScript, images
- \`app.py\` - Flask application with all routes
- \`requirements.txt\` - Python dependencies
- \`demo_all_pages.html\` - Complete demo page

## Technologies

- Flask (Python web framework)
- Bootstrap 5.2.3
- Font Awesome 6.2.1
- Custom CSS with purple theme
- Responsive JavaScript functionality

Uploaded from Replit workspace.`;

    console.log('Creating README.md...');
    const readmeResult = await uploadFileToGitHub(octokit, owner, repo, 'README.md', readmeContent);
    
    if (!readmeResult.success) {
      throw new Error(`Failed to create README: ${readmeResult.error}`);
    }
    
    console.log('✅ README.md created successfully');

    // Get all files from the website package
    const allFiles = getAllFiles(sourcePath);
    console.log(`Found ${allFiles.length} files to upload...`);

    let successCount = 0;
    let errorCount = 0;

    // Upload files one by one
    for (let i = 0; i < allFiles.length; i++) {
      const filePath = allFiles[i];
      const relativePath = relative(sourcePath, filePath);
      
      console.log(`[${i + 1}/${allFiles.length}] Uploading: ${relativePath}`);
      
      try {
        const content = readFileSync(filePath);
        const isBase64 = relativePath.match(/\.(png|jpg|jpeg|gif|ico|mp3|wav|zip|pdf)$/i);
        
        const result = await uploadFileToGitHub(
          octokit, 
          owner, 
          repo, 
          relativePath, 
          isBase64 ? content.toString('base64') : content.toString(),
          isBase64
        );
        
        if (result.success) {
          successCount++;
        } else {
          console.error(`❌ Failed: ${relativePath} - ${result.error}`);
          errorCount++;
        }
        
        // Add small delay to avoid rate limiting
        if (i % 10 === 0 && i > 0) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
      } catch (error) {
        console.error(`❌ Error processing ${relativePath}:`, error.message);
        errorCount++;
      }
    }

    console.log('\\n🎉 Upload completed!');
    console.log(`✅ Successfully uploaded: ${successCount + 1} files (including README)`);
    console.log(`❌ Failed uploads: ${errorCount} files`);
    console.log(`🔗 Repository: https://github.com/${owner}/${repo}`);
    
    return {
      success: true,
      url: `https://github.com/${owner}/${repo}`,
      successCount: successCount + 1,
      errorCount
    };

  } catch (error) {
    console.error('❌ Error pushing to GitHub:', error.message);
    throw error;
  }
}

// Run the push
pushToGitHub()
  .then(result => {
    console.log('\\n📊 Final Summary:');
    console.log(`🎯 Repository: ${result.url}`);
    console.log(`✅ Files uploaded: ${result.successCount}`);
    console.log(`❌ Failed uploads: ${result.errorCount}`);
    console.log('\\n🚀 Website UI package successfully pushed to GitHub!');
    process.exit(0);
  })
  .catch(error => {
    console.error('💥 Push failed:', error);
    process.exit(1);
  });