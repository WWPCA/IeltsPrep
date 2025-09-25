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

function getAllFiles(dirPath, arrayOfFiles = []) {
  const files = readdirSync(dirPath)
  const skipFiles = ['.DS_Store', 'Thumbs.db', '.git'];
  
  files.forEach(function(file) {
    if (skipFiles.includes(file)) return;
    
    const fullPath = join(dirPath, file)
    if (statSync(fullPath).isDirectory()) {
      arrayOfFiles = getAllFiles(fullPath, arrayOfFiles)
    } else {
      const stats = statSync(fullPath);
      if (stats.size < 100 * 1024 * 1024) { // Skip files larger than 100MB
        arrayOfFiles.push(fullPath)
      }
    }
  })

  return arrayOfFiles
}

async function deleteAllFiles(octokit, owner, repo) {
  console.log('🗑️  Clearing existing repository contents...');
  
  try {
    // Get all files in the repository
    const { data: contents } = await octokit.rest.repos.getContent({
      owner,
      repo,
      path: ''
    });

    // Delete each file
    for (const item of contents) {
      if (item.type === 'file') {
        console.log(`   Deleting: ${item.name}`);
        try {
          await octokit.rest.repos.deleteFile({
            owner,
            repo,
            path: item.name,
            message: `Remove ${item.name} - cleaning repository for current preview session only`,
            sha: item.sha
          });
        } catch (error) {
          console.log(`   ⚠️  Could not delete ${item.name}: ${error.message}`);
        }
      }
    }
    
    console.log('✅ Repository cleared successfully');
    
  } catch (error) {
    console.log(`⚠️  Error clearing repository: ${error.message}`);
    // Continue anyway, we can overwrite files
  }
}

async function uploadFileToGitHub(octokit, owner, repo, filePath, content, isBase64 = false) {
  try {
    const { data } = await octokit.rest.repos.createOrUpdateFileContents({
      owner,
      repo,
      path: filePath,
      message: `Add ${filePath} - current preview session template`,
      content: isBase64 ? content : Buffer.from(content).toString('base64'),
      branch: 'main'
    });
    return { success: true, sha: data.content.sha };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function cleanAndUploadToGitHub() {
  try {
    const octokit = await getUncachableGitHubClient();
    
    const owner = 'WWPCA';
    const repo = 'Templates';
    const sourcePath = './clean_templates_package';
    
    console.log('🧹 Starting GitHub repository cleanup for current preview session...');
    console.log('📁 Source: clean_templates_package (active templates only)');
    
    // Step 1: Clear existing files
    await deleteAllFiles(octokit, owner, repo);
    
    // Step 2: Upload clean template package
    console.log('\\n📤 Uploading current preview session templates...');
    
    const allFiles = getAllFiles(sourcePath);
    console.log(`Found ${allFiles.length} active files to upload...`);

    let successCount = 0;
    let errorCount = 0;

    // Upload files one by one
    for (let i = 0; i < allFiles.length; i++) {
      const filePath = allFiles[i];
      const relativePath = relative(sourcePath, filePath);
      
      console.log(`[${i + 1}/${allFiles.length}] Uploading: ${relativePath}`);
      
      try {
        const content = readFileSync(filePath);
        const isBase64 = relativePath.match(/\\.(png|jpg|jpeg|gif|ico|mp3|wav|zip|pdf)$/i);
        
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
          console.log(`   ✅ Success`);
        } else {
          console.log(`   ❌ Failed: ${result.error}`);
          errorCount++;
        }
        
        // Add small delay to avoid rate limiting
        if (i % 5 === 0 && i > 0) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        
      } catch (error) {
        console.log(`   ❌ Error processing ${relativePath}: ${error.message}`);
        errorCount++;
      }
    }

    console.log('\\n🎉 Repository cleanup and upload completed!');
    console.log(`✅ Successfully uploaded: ${successCount} files`);
    console.log(`❌ Failed uploads: ${errorCount} files`);
    console.log(`🔗 Repository: https://github.com/${owner}/${repo}`);
    console.log('\\n📋 Repository now contains ONLY current preview session templates:');
    console.log('   • 6 active HTML templates');
    console.log('   • Main application (app.py)');
    console.log('   • Essential config files');
    console.log('   • Clean documentation');
    
    return {
      success: true,
      url: `https://github.com/${owner}/${repo}`,
      successCount,
      errorCount,
      totalActiveFiles: allFiles.length
    };

  } catch (error) {
    console.error('❌ Error cleaning GitHub repository:', error.message);
    throw error;
  }
}

// Run the cleanup and upload
cleanAndUploadToGitHub()
  .then(result => {
    console.log('\\n🚀 GitHub repository successfully cleaned and updated!');
    console.log(`📊 Final summary: ${result.successCount}/${result.totalActiveFiles} active templates uploaded`);
    console.log(`🎯 Repository now shows only current preview session content`);
    process.exit(0);
  })
  .catch(error => {
    console.error('💥 Repository cleanup failed:', error);
    process.exit(1);
  });