# this file will scan the _posts folder and Git stage the deletion of old files
# the max_age_days variable at the top of the file defines how old of files we will keep

from datetime import datetime, timedelta
from pathlib import Path
from subprocess import check_call

max_age_days = 1

current_time = datetime.now()
cutoff_date = current_time - timedelta(days=max_age_days)

this_file_path = Path(__file__).resolve()
repo_root = this_file_path.parent.parent
posts_folder = repo_root / '_posts'
all_posts = posts_folder.glob('**/*.html')
all_posts_list = list(all_posts)
num_to_delete = 0
for post in all_posts_list:
    measurement_time = datetime.now()
    try:
        file_name = post.name
        time_string = file_name.split('_')[0]
        measurement_time = datetime.strptime(time_string, '%Y-%m-%d-%H-%M-%S')
    except Exception as e:
        print(f"Could not create timestamp for file: \"{post}\"; Reason: {e}")
    if measurement_time < cutoff_date:
        check_call(['git', 'rm', post])
        num_to_delete += 1
if num_to_delete > 0:
    print(f"{num_to_delete} file(s) staged for deletion, next `git commit -m MSG` and `git push origin main`")
else:
    print("No files were staged for deletion, nothing to do")