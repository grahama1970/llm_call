const puppeteer = require('puppeteer');

async function takeScreenshot() {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Navigate to the improved report
    console.log('Navigating to report...');
    await page.goto('http://localhost:8888/llm-call-verification-improved.html', {
      waitUntil: 'networkidle2'
    });
    
    // Wait for content to load
    await page.waitForSelector('h1', { timeout: 5000 });
    
    // Take full page screenshot
    console.log('Taking screenshot...');
    await page.screenshot({
      path: 'verification-report-screenshot.png',
      fullPage: true
    });
    
    console.log('Screenshot saved to verification-report-screenshot.png');
    
    // Analyze the page
    const analysis = await page.evaluate(() => {
      const results = {
        title: document.querySelector('h1')?.textContent || 'No title found',
        totalTests: document.querySelector('.text-4xl')?.textContent || '0',
        tables: document.querySelectorAll('table').length,
        codeBlocks: document.querySelectorAll('pre').length,
        buttons: document.querySelectorAll('button').length,
        colorScheme: {
          hasGradients: document.querySelectorAll('[class*="gradient"]').length > 0,
          primaryColors: []
        }
      };
      
      // Check for accessibility
      results.accessibility = {
        hasSkipLink: !!document.querySelector('a[href="#main-content"]'),
        hasFocusStyles: !!document.querySelector('style')?.textContent.includes(':focus'),
        hasAltText: Array.from(document.querySelectorAll('img')).every(img => img.alt)
      };
      
      return results;
    });
    
    console.log('\nPage Analysis:');
    console.log(JSON.stringify(analysis, null, 2));
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

takeScreenshot().catch(console.error);