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

// Function to recursively get all files in a directory
function getAllFiles(dirPath, arrayOfFiles = []) {
  const files = readdirSync(dirPath)

  files.forEach(function(file) {
    const fullPath = join(dirPath, file)
    if (statSync(fullPath).isDirectory()) {
      arrayOfFiles = getAllFiles(fullPath, arrayOfFiles)
    } else {
      arrayOfFiles.push(fullPath)
    }
  })

  return arrayOfFiles
}

async function pushToGitHub() {
  try {
    const octokit = await getUncachableGitHubClient();
    
    const owner = 'WWPCA';
    const repo = 'Templates';
    const sourcePath = './website_ui_package';
    
    console.log('Starting GitHub push...');
    
    // Get the latest commit SHA from main branch
    let latestCommitSha;
    try {
      const { data: refData } = await octokit.rest.git.getRef({
        owner,
        repo,
        ref: 'heads/main'
      });
      latestCommitSha = refData.object.sha;
    } catch (error) {
      if (error.status === 404) {
        // Repository might be empty, we'll create an initial commit
        console.log('Repository appears to be empty, creating initial commit');
        latestCommitSha = null;
      } else {
        throw error;
      }
    }

    // Get all files from the website package
    const allFiles = getAllFiles(sourcePath);
    const fileBlobs = [];

    console.log(`Processing ${allFiles.length} files...`);

    // Create blobs for all files
    for (const filePath of allFiles) {
      const relativePath = relative(sourcePath, filePath);
      console.log(`Processing: ${relativePath}`);
      
      try {
        const content = readFileSync(filePath);
        const { data: blobData } = await octokit.rest.git.createBlob({
          owner,
          repo,
          content: content.toString('base64'),
          encoding: 'base64'
        });
        
        fileBlobs.push({
          path: relativePath,
          mode: '100644',
          type: 'blob',
          sha: blobData.sha
        });
      } catch (error) {
        console.error(`Error processing file ${relativePath}:`, error.message);
      }
    }

    console.log(`Created ${fileBlobs.length} blobs`);

    // Create tree
    const { data: treeData } = await octokit.rest.git.createTree({
      owner,
      repo,
      tree: fileBlobs,
      base_tree: latestCommitSha ? undefined : null
    });

    console.log('Created tree');

    // Create commit
    const { data: commitData } = await octokit.rest.git.createCommit({
      owner,
      repo,
      message: 'Add IELTS GenAI Prep Complete Website UI Package\n\nIncludes:\n- 97+ HTML templates\n- Complete CSS and JavaScript\n- All static assets and images\n- Flask application with all routes\n- robots.txt and sitemap.xml\n- Professional responsive design',
      tree: treeData.sha,
      parents: latestCommitSha ? [latestCommitSha] : []
    });

    console.log('Created commit');

    // Update reference
    await octokit.rest.git.updateRef({
      owner,
      repo,
      ref: 'heads/main',
      sha: commitData.sha
    });

    console.log('✅ Successfully pushed to GitHub!');
    console.log(`🔗 Repository: https://github.com/${owner}/${repo}`);
    console.log(`📝 Commit: ${commitData.sha}`);
    
    return {
      success: true,
      url: `https://github.com/${owner}/${repo}`,
      commit: commitData.sha,
      filesCount: fileBlobs.length
    };

  } catch (error) {
    console.error('❌ Error pushing to GitHub:', error.message);
    throw error;
  }
}

// Run the push
pushToGitHub()
  .then(result => {
    console.log('Push completed successfully:', result);
    process.exit(0);
  })
  .catch(error => {
    console.error('Push failed:', error);
    process.exit(1);
  });