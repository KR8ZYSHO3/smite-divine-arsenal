import psutil
import time

def is_webdriver_chrome(process):
    """Check if a Chrome process is likely a WebDriver process"""
    try:
        cmdline = process.cmdline()
        if not cmdline:
            return False
            
        # Look for WebDriver-specific command line arguments
        webdriver_indicators = [
            '--remote-debugging-port=',
            '--test-type=webdriver',
            '--disable-extensions',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--headless',
            '--user-data-dir=',
            '--port='
        ]
        
        cmdline_str = ' '.join(cmdline)
        
        # Check if it has multiple WebDriver indicators
        indicator_count = sum(1 for indicator in webdriver_indicators if indicator in cmdline_str)
        
        # Also check for common WebDriver patterns
        if indicator_count >= 2:  # Multiple indicators suggest WebDriver
            return True
            
        # Check for specific WebDriver patterns
        if ('--remote-debugging-port=' in cmdline_str and 
            ('--test-type' in cmdline_str or '--disable-extensions' in cmdline_str)):
            return True
            
        return False
        
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def view_chrome_processes():
    """View all Chrome processes without killing any"""
    webdriver_processes = []
    regular_chrome_processes = []
    
    for process in psutil.process_iter():
        try:
            if process.name() and 'chrome' in process.name().lower():
                if is_webdriver_chrome(process):
                    webdriver_processes.append(process)
                else:
                    regular_chrome_processes.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    print("=" * 60)
    print("🔍 CHROME PROCESS VIEWER (READ-ONLY)")
    print("=" * 60)
    
    if regular_chrome_processes:
        print(f"\n✅ YOUR REGULAR CHROME BROWSERS ({len(regular_chrome_processes)} processes):")
        total_regular_memory = 0
        for i, process in enumerate(regular_chrome_processes, 1):
            try:
                memory_mb = process.memory_info().rss / (1024 * 1024)
                total_regular_memory += memory_mb
                print(f"  {i}. PID: {process.pid}, Memory: {memory_mb:.2f} MB")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"  {i}. PID: {process.pid}, Memory: N/A")
        print(f"  Total Memory: {total_regular_memory:.2f} MB")
    else:
        print(f"\n✅ YOUR REGULAR CHROME BROWSERS: None running")
    
    if webdriver_processes:
        print(f"\n⚠️ WEBDRIVER CHROME PROCESSES ({len(webdriver_processes)} processes):")
        total_webdriver_memory = 0
        for i, process in enumerate(webdriver_processes, 1):
            try:
                memory_mb = process.memory_info().rss / (1024 * 1024)
                total_webdriver_memory += memory_mb
                cmdline = ' '.join(process.cmdline()[:3])  # Show first 3 parts of command line
                print(f"  {i}. PID: {process.pid}, Memory: {memory_mb:.2f} MB")
                print(f"     Command: {cmdline}...")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"  {i}. PID: {process.pid}, Memory: N/A")
        print(f"  Total Memory: {total_webdriver_memory:.2f} MB")
        print(f"  ⚠️ These are likely from the Divine Arsenal application")
    else:
        print(f"\n✅ WEBDRIVER CHROME PROCESSES: None found")
    
    print("\n" + "=" * 60)
    print("📝 NOTE: This script only VIEWS processes, it doesn't kill anything.")
    print("   Your Chrome browsers are completely safe.")
    print("=" * 60)

if __name__ == "__main__":
    view_chrome_processes() 