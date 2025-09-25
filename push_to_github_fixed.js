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
    
    // Check if repository is empty by trying to get main branch
    let isEmptyRepo = false;
    try {
      await octokit.rest.git.getRef({
        owner,
        repo,
        ref: 'heads/main'
      });
    } catch (error) {
      if (error.status === 409 || error.status === 404) {
        isEmptyRepo = true;
        console.log('Repository is empty, creating initial commit');
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

    // Create tree (no base tree for empty repo)
    const { data: treeData } = await octokit.rest.git.createTree({
      owner,
      repo,
      tree: fileBlobs
    });

    console.log('Created tree');

    // Create commit (no parents for empty repo)
    const { data: commitData } = await octokit.rest.git.createCommit({
      owner,
      repo,
      message: 'Add IELTS GenAI Prep Complete Website UI Package\n\nIncludes:\n- 97+ HTML templates and pages\n- Complete CSS styling with purple theme\n- Interactive JavaScript functionality\n- All static assets and images\n- Flask application with all routes\n- robots.txt and sitemap.xml\n- Professional responsive design\n- TrueScore® and ClearScore® branding\n\nFeatures:\n✅ Home page with hero section\n✅ Assessment product pages\n✅ Practice test interfaces\n✅ GDPR compliance pages\n✅ Admin dashboard\n✅ Mobile responsive design\n✅ SEO optimized',
      tree: treeData.sha,
      parents: [] // Empty array for initial commit
    });

    console.log('Created initial commit');

    // Create the main branch reference
    await octokit.rest.git.createRef({
      owner,
      repo,
      ref: 'refs/heads/main',
      sha: commitData.sha
    });

    console.log('✅ Successfully pushed to GitHub!');
    console.log(`🔗 Repository: https://github.com/${owner}/${repo}`);
    console.log(`📝 Commit: ${commitData.sha}`);
    console.log(`📁 Files uploaded: ${fileBlobs.length}`);
    
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
    console.log('🎉 Push completed successfully!');
    console.log(`📊 Summary: ${result.filesCount} files uploaded to ${result.url}`);
    process.exit(0);
  })
  .catch(error => {
    console.error('💥 Push failed:', error);
    process.exit(1);
  });