env_dir=./cluster_env
python_version="3.6.1"

module load python_gpu/$python_version cuda/9.0.176 cudnn/7.0

if [ ! -d "$env_dir" ]; then
    python -m pip install --user virtualenv
    python -m virtualenv \
        --system-site-packages \
        --python="/cluster/apps/python/$python_version/bin/python" \
        "$env_dir"
fi

source "$env_dir/bin/activate"
