# JupyterLab with persistent scientific Python

[JupyterLab](https://jupyter.org/) with NumPy, pandas, SciPy, matplotlib, and scikit-learn on Railway. This single-user template builds a small wrapper over the official scipy-notebook image, pinned by version and digest.

## Deploy and sign in

1. Deploy the template and wait for the `/login` healthcheck.
2. Copy the generated `JUPYTER_TOKEN` from the service's Variables panel.
3. Open the service's HTTPS domain and paste the token into the login form.
4. Create a Python notebook from the Launcher and run a cell.

Keep the token private. Anyone with it can run code and access this service's files and environment. This is a single-user development workspace, not a multi-tenant notebook service. Empty or whitespace-only tokens fail startup. Password changes on the login form are disabled so a saved password cannot bypass a later token rotation. Rotate the token in Railway Variables and redeploy when needed.

## Runtime and storage

The base image is `quay.io/jupyter/scipy-notebook:2026-09-07`, pinned to `sha256:ec7343ba248a7473c42322e86e7157bef9ebc9253c40a88e573b3fcf607a9a8a`.

The inherited image entrypoint starts as root to repair volume ownership, then runs Jupyter as `jovyan`, UID 1000. The wrapper rejects a root notebook process. Leave `RAILWAY_RUN_UID` unset. No passwordless sudo is granted.

| Path | Lifetime |
| --- | --- |
| `/home/jovyan` | Railway volume: notebooks, datasets, settings, and user-installed Python packages survive redeploys. |
| `/tmp/jupyter-runtime` | Temporary runtime files, recreated with normal permission checks. |
| `/opt/conda` | Image packages, replaced on redeploy. |

A `lost+found` directory on a new Railway volume is normal. Deleting the volume deletes the workspace. A volume is not a backup; export notebooks and back up important data separately. Budget for the large scientific Python image and at least 1 GB memory, then increase resources for your workloads.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `JUPYTER_TOKEN` | `${{secret()}}` | Required generated login credential. |
| `PORT` | Railway-provided, or `8888` locally | HTTP listener, with no silent port fallback. |
| `PYTHONUSERBASE` | `/home/jovyan/.local` in the image | Persistent location for `pip install --user`. |
| `JUPYTER_RUNTIME_DIR` | `/tmp/jupyter-runtime` in the image | Keeps runtime sockets and permission-sensitive files off the volume. |

The server listens on `0.0.0.0`. Railway terminates HTTPS. Forwarded headers are trusted for this deployment. Cross-origin access stays disabled by default. The `/login` deployment healthcheck verifies the web server, not notebook kernel execution. Notebook execution and persistence require separate functional tests.

## Persistent Python packages

In a Jupyter terminal:

```bash
pip install --user <package>
python -c "import site; print(site.getusersitepackages())"
```

Restart the notebook kernel after installing a package. Image-level installs under `/opt/conda` do not survive redeployment; put reproducible environment changes in your fork's Dockerfile.

## Local checks

```bash
python3 -m unittest discover -s . -p 'test_*.py'
bash -n railway-start.sh
```

The wrapper tests cover required tokens, valid port overrides, and authentication defaults. They do not replace deployment and browser tests.

Jupyter Docker Stacks and JupyterLab are distributed under BSD licenses. Included scientific packages have their own upstream licenses.
