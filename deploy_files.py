import os
import shutil

def deploy_system_files():
    """Deploy system files to their proper locations"""
    print("=== Deploying System Files ===")
    
    # Define source files and their destinations
    files_to_deploy = {
        'core': [
            'payment_system_v4.py',  # Main system file
            'validation_system.py',   # Input validation
            'file_operations.py',     # File handling
            'status_tracker.py',      # Status tracking
            'exception_handler.py',   # Exception handling
            'audit_trail.py',         # Audit logging
        ],
        'deployment': [
            'deploy_system.py',       # System deployment
            'deploy_files.py',        # File deployment
        ]
    }
    
    try:
        # Create src directory if it doesn't exist
        src_dir = os.path.join('src')
        os.makedirs(src_dir, exist_ok=True)
        print(f"Created source directory: {src_dir}")
        
        # Move core files to src
        print("\nMoving core files to src directory:")
        for file in files_to_deploy['core']:
            if os.path.exists(file):
                shutil.copy2(file, os.path.join(src_dir, file))
                print(f"SUCCESS: Moved {file}")
        
        # Rename main system file
        main_system = os.path.join(src_dir, 'payment_system_v4.py')
        if os.path.exists(main_system):
            new_name = os.path.join(src_dir, 'payment_system.py')
            shutil.copy2(main_system, new_name)
            print(f"SUCCESS: Created main system file: payment_system.py")
        
        # Create __init__.py in src directory
        init_file = os.path.join(src_dir, '__init__.py')
        with open(init_file, 'w') as f:
            f.write('# Payment System Module\n')
        print(f"SUCCESS: Created {init_file}")
        
        # Remove old version files
        old_versions = [
            'payment-system.py',
            'payment_system_v2.py',
            'payment_system_v3.py'
        ]
        print("\nCleaning up old versions:")
        for old_file in old_versions:
            if os.path.exists(old_file):
                os.remove(old_file)
                print(f"SUCCESS: Removed {old_file}")
        
        print("\nSystem files deployed successfully!")
        return True
        
    except Exception as e:
        print(f"Error deploying system files: {str(e)}")
        return False

if __name__ == "__main__":
    deploy_system_files()
