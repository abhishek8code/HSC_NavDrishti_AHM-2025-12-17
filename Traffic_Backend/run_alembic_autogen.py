from alembic.config import Config
from alembic import command
import os

repo_root = os.path.dirname(os.path.abspath(__file__))
conf_path = os.path.join(repo_root, 'alembic.ini')
cfg = Config(conf_path)
# ensure script_location points to the local alembic folder (absolute path)
cfg.set_main_option('script_location', os.path.join(repo_root, 'alembic'))

# Autogenerate a revision and stamp head. If no changes, revision may be empty.
command.revision(cfg, message='initial', autogenerate=True)
command.stamp(cfg, 'head')
print('Alembic revision created and stamped')
