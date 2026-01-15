const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');

// Create a professional IPC APP icon
function generateIcon(size, filename) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');

  // Background gradient (dark blue to purple)
  const gradient = ctx.createLinearGradient(0, 0, size, size);
  gradient.addColorStop(0, '#1a1a2e');
  gradient.addColorStop(0.5, '#16213e');
  gradient.addColorStop(1, '#0f3460');
  
  // Draw rounded rectangle background
  const radius = size * 0.2;
  ctx.beginPath();
  ctx.roundRect(0, 0, size, size, radius);
  ctx.fillStyle = gradient;
  ctx.fill();

  // Draw shield shape (legal symbol)
  const centerX = size / 2;
  const centerY = size / 2;
  const shieldSize = size * 0.55;
  
  ctx.beginPath();
  ctx.moveTo(centerX, centerY - shieldSize/2);
  ctx.lineTo(centerX + shieldSize/2, centerY - shieldSize/3);
  ctx.lineTo(centerX + shieldSize/2, centerY + shieldSize/6);
  ctx.quadraticCurveTo(centerX, centerY + shieldSize/2, centerX, centerY + shieldSize/2);
  ctx.quadraticCurveTo(centerX, centerY + shieldSize/2, centerX - shieldSize/2, centerY + shieldSize/6);
  ctx.lineTo(centerX - shieldSize/2, centerY - shieldSize/3);
  ctx.closePath();
  
  // Shield gradient
  const shieldGradient = ctx.createLinearGradient(centerX - shieldSize/2, centerY - shieldSize/2, centerX + shieldSize/2, centerY + shieldSize/2);
  shieldGradient.addColorStop(0, '#e94560');
  shieldGradient.addColorStop(1, '#ff6b6b');
  ctx.fillStyle = shieldGradient;
  ctx.fill();
  
  // Add white border to shield
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = size * 0.02;
  ctx.stroke();

  // Draw balance scale icon inside shield
  const scaleY = centerY - size * 0.05;
  const scaleWidth = size * 0.25;
  
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = size * 0.025;
  ctx.lineCap = 'round';
  
  // Vertical pole
  ctx.beginPath();
  ctx.moveTo(centerX, scaleY - size * 0.12);
  ctx.lineTo(centerX, scaleY + size * 0.15);
  ctx.stroke();
  
  // Horizontal bar
  ctx.beginPath();
  ctx.moveTo(centerX - scaleWidth/2, scaleY - size * 0.08);
  ctx.lineTo(centerX + scaleWidth/2, scaleY - size * 0.08);
  ctx.stroke();
  
  // Left pan
  ctx.beginPath();
  ctx.arc(centerX - scaleWidth/2, scaleY + size * 0.02, size * 0.06, 0, Math.PI);
  ctx.stroke();
  
  // Right pan
  ctx.beginPath();
  ctx.arc(centerX + scaleWidth/2, scaleY + size * 0.02, size * 0.06, 0, Math.PI);
  ctx.stroke();
  
  // Strings
  ctx.beginPath();
  ctx.moveTo(centerX - scaleWidth/2, scaleY - size * 0.08);
  ctx.lineTo(centerX - scaleWidth/2 - size * 0.06, scaleY + size * 0.02);
  ctx.moveTo(centerX - scaleWidth/2, scaleY - size * 0.08);
  ctx.lineTo(centerX - scaleWidth/2 + size * 0.06, scaleY + size * 0.02);
  ctx.stroke();
  
  ctx.beginPath();
  ctx.moveTo(centerX + scaleWidth/2, scaleY - size * 0.08);
  ctx.lineTo(centerX + scaleWidth/2 - size * 0.06, scaleY + size * 0.02);
  ctx.moveTo(centerX + scaleWidth/2, scaleY - size * 0.08);
  ctx.lineTo(centerX + scaleWidth/2 + size * 0.06, scaleY + size * 0.02);
  ctx.stroke();

  // Add "IPC" text at bottom of shield
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${size * 0.1}px Arial`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('IPC', centerX, centerY + size * 0.18);

  // Save the image
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(path.join(__dirname, 'assets', filename), buffer);
  console.log(`Generated: ${filename}`);
}

// Generate all required icons
console.log('Generating app icons...');
generateIcon(1024, 'icon.png');
generateIcon(1024, 'adaptive-icon.png');
generateIcon(48, 'favicon.png');

// Generate splash screen
function generateSplash() {
  const canvas = createCanvas(1284, 2778);
  const ctx = canvas.getContext('2d');

  // Background gradient
  const gradient = ctx.createLinearGradient(0, 0, 1284, 2778);
  gradient.addColorStop(0, '#1a1a2e');
  gradient.addColorStop(0.5, '#16213e');
  gradient.addColorStop(1, '#0f3460');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 1284, 2778);

  // Draw the same icon in center
  const iconSize = 400;
  const centerX = 1284 / 2;
  const centerY = 2778 / 2 - 100;
  
  // Shield
  const shieldSize = iconSize * 0.55;
  ctx.beginPath();
  ctx.moveTo(centerX, centerY - shieldSize/2);
  ctx.lineTo(centerX + shieldSize/2, centerY - shieldSize/3);
  ctx.lineTo(centerX + shieldSize/2, centerY + shieldSize/6);
  ctx.quadraticCurveTo(centerX, centerY + shieldSize/2, centerX, centerY + shieldSize/2);
  ctx.quadraticCurveTo(centerX, centerY + shieldSize/2, centerX - shieldSize/2, centerY + shieldSize/6);
  ctx.lineTo(centerX - shieldSize/2, centerY - shieldSize/3);
  ctx.closePath();
  
  const shieldGradient = ctx.createLinearGradient(centerX - shieldSize/2, centerY - shieldSize/2, centerX + shieldSize/2, centerY + shieldSize/2);
  shieldGradient.addColorStop(0, '#e94560');
  shieldGradient.addColorStop(1, '#ff6b6b');
  ctx.fillStyle = shieldGradient;
  ctx.fill();
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 4;
  ctx.stroke();

  // Scale icon
  const scaleY = centerY - 20;
  const scaleWidth = iconSize * 0.25;
  
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 8;
  ctx.lineCap = 'round';
  
  ctx.beginPath();
  ctx.moveTo(centerX, scaleY - 50);
  ctx.lineTo(centerX, scaleY + 60);
  ctx.stroke();
  
  ctx.beginPath();
  ctx.moveTo(centerX - scaleWidth/2, scaleY - 30);
  ctx.lineTo(centerX + scaleWidth/2, scaleY - 30);
  ctx.stroke();
  
  ctx.beginPath();
  ctx.arc(centerX - scaleWidth/2, scaleY + 10, 25, 0, Math.PI);
  ctx.stroke();
  
  ctx.beginPath();
  ctx.arc(centerX + scaleWidth/2, scaleY + 10, 25, 0, Math.PI);
  ctx.stroke();

  // IPC text
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 50px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('IPC', centerX, centerY + 80);

  // App name below
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 60px Arial';
  ctx.fillText('IPC APP', centerX, centerY + 250);
  
  ctx.font = '30px Arial';
  ctx.fillStyle = 'rgba(255,255,255,0.7)';
  ctx.fillText('Indian Penal Code 1860', centerX, centerY + 310);

  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(path.join(__dirname, 'assets', 'splash.png'), buffer);
  console.log('Generated: splash.png');
}

generateSplash();
console.log('All icons generated successfully!');
