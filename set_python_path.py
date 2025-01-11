import os
import site
import sys

def add_to_python_path():
    """Add src directory to Python path"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    
    if src_dir not in sys.path:
        # Add to system path
        sys.path.append(src_dir)
        print(f"Added {src_dir} to Python path")
        
        # Create .pth file in site-packages
        site_packages = site.getsitepackages()[0]
        pth_file = os.path.join(site_packages, 'payment_system.pth')
        
        try:
            with open(pth_file, 'w') as f:
                f.write(src_dir)
            print(f"Created {pth_file}")
            print("Python path setup completed successfully!")
            return True
        except Exception as e:
            print(f"Error creating .pth file: {str(e)}")
            return False
    else:
        print(f"{src_dir} already in Python path")
        return True

if __name__ == "__main__":
    add_to_python_path()
