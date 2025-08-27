import os
import subprocess
import random
from datetime import datetime, timedelta

# Configuration
TOTAL_COMMITS = 200
START_DATE = datetime(2025, 8, 27)  # August 27, 2025
END_DATE = datetime(2025, 10, 1)    # October 1, 2025
REPO_PATH = r"J:\VS smart attendance\Smart_attendance_system"

# Commit message templates
COMMIT_MESSAGES = [
    "Update documentation",
    "Fix typo in comments",
    "Improve code formatting",
    "Add error handling",
    "Refactor function logic",
    "Update dependencies",
    "Enhance logging",
    "Optimize performance",
    "Add code comments",
    "Update README",
    "Fix minor bug",
    "Improve user interface",
    "Add validation checks",
    "Update configuration",
    "Enhance security",
    "Improve database queries",
    "Add feature enhancement",
    "Update templates",
    "Refactor code structure",
    "Add unit tests",
    "Update requirements",
    "Improve error messages",
    "Add input validation",
    "Update styling",
    "Enhance face recognition",
    "Improve attendance tracking",
    "Add admin features",
    "Update user registration",
    "Improve database schema",
    "Add API endpoints",
]

# Files to modify
FILES_TO_MODIFY = [
    "README.md",
    "app.py",
    "attendance_system.py",
    "config.py",
    "database.py",
    "face_recognition_model.py",
    "register_user.py",
    "requirements.txt",
]

def get_commit_distribution(total_commits, start_date, end_date):
    """Distribute commits across the date range with realistic patterns"""
    total_days = (end_date - start_date).days + 1
    commits_per_day = []
    
    remaining_commits = total_commits
    current_date = start_date
    
    while current_date <= end_date:
        # Weekday (0-4) vs Weekend (5-6)
        is_weekend = current_date.weekday() >= 5
        
        if remaining_commits > 0:
            if is_weekend:
                # Fewer commits on weekends
                commits = random.randint(1, min(4, remaining_commits))
            else:
                # More commits on weekdays
                commits = random.randint(3, min(8, remaining_commits))
            
            # Adjust for remaining commits
            days_left = (end_date - current_date).days + 1
            if days_left > 0:
                avg_needed = remaining_commits / days_left
                commits = min(commits, int(avg_needed * 1.5))
            
            commits_per_day.append((current_date, commits))
            remaining_commits -= commits
        else:
            commits_per_day.append((current_date, 0))
        
        current_date += timedelta(days=1)
    
    # Distribute any remaining commits
    while remaining_commits > 0:
        day_idx = random.randint(0, len(commits_per_day) - 1)
        date, count = commits_per_day[day_idx]
        commits_per_day[day_idx] = (date, count + 1)
        remaining_commits -= 1
    
    return commits_per_day

def make_file_change(file_path):
    """Make a small change to a file"""
    if not os.path.exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Add a comment or newline
    if file_path.endswith('.py'):
        # Add a comment
        comment = f"\n# Updated: {datetime.now().strftime('%Y-%m-%d')}\n"
        content += comment
    elif file_path.endswith('.md'):
        # Add a newline or update timestamp
        content += f"\n<!-- Updated: {datetime.now().strftime('%Y-%m-%d')} -->\n"
    elif file_path.endswith('.txt'):
        # Add a comment
        content += f"\n# Updated: {datetime.now().strftime('%Y-%m-%d')}\n"
    else:
        # Just add a newline
        content += "\n"
    
    with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(content)
    
    return True

def create_commit(date, time_str, message):
    """Create a commit with a specific date"""
    # Format: "YYYY-MM-DD HH:MM:SS"
    commit_date = f"{date.strftime('%Y-%m-%d')} {time_str}"
    
    # Set environment variables for commit date
    env = os.environ.copy()
    env['GIT_AUTHOR_DATE'] = commit_date
    env['GIT_COMMITTER_DATE'] = commit_date
    
    # Add changes
    subprocess.run(['git', 'add', '.'], cwd=REPO_PATH, env=env, check=True)
    
    # Create commit
    subprocess.run(
        ['git', 'commit', '-m', message],
        cwd=REPO_PATH,
        env=env,
        check=True,
        capture_output=True
    )

def main():
    print(f"Generating {TOTAL_COMMITS} commits from {START_DATE.date()} to {END_DATE.date()}")
    print(f"Repository: {REPO_PATH}\n")
    
    # Get commit distribution
    commits_per_day = get_commit_distribution(TOTAL_COMMITS, START_DATE, END_DATE)
    
    total_generated = 0
    
    for date, num_commits in commits_per_day:
        if num_commits == 0:
            continue
        
        print(f"{date.strftime('%Y-%m-%d')} ({date.strftime('%A')}): {num_commits} commits")
        
        for i in range(num_commits):
            # Random time during the day (working hours: 9 AM - 11 PM)
            hour = random.randint(9, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
            
            # Select random file to modify
            file_to_modify = random.choice(FILES_TO_MODIFY)
            file_path = os.path.join(REPO_PATH, file_to_modify)
            
            # Make a change
            if make_file_change(file_path):
                # Create commit
                message = random.choice(COMMIT_MESSAGES)
                try:
                    create_commit(date, time_str, message)
                    total_generated += 1
                    print(f"  [{total_generated}/{TOTAL_COMMITS}] {time_str} - {message}")
                except subprocess.CalledProcessError as e:
                    print(f"  Error creating commit: {e}")
    
    print(f"\n✓ Successfully generated {total_generated} commits!")
    print("\nVerifying commits...")
    
    # Verify
    result = subprocess.run(
        ['git', 'rev-list', '--count', 'HEAD'],
        cwd=REPO_PATH,
        capture_output=True,
        text=True
    )
    print(f"Total commits in repository: {result.stdout.strip()}")
    
    # Show date range
    result = subprocess.run(
        ['git', 'log', '--pretty=format:%ai', '--reverse'],
        cwd=REPO_PATH,
        capture_output=True,
        text=True
    )
    dates = result.stdout.strip().split('\n')
    if dates:
        print(f"First commit date: {dates[0]}")
        print(f"Last commit date: {dates[-1]}")

if __name__ == "__main__":
    main()
