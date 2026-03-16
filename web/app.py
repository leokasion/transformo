from flask import Flask, request, render_template, flash, redirect, url_for, send_from_directory
from markupsafe import Markup
import os
import base64

app = Flask(__name__)
app.secret_key = 'devops_secret_key'

# Configs from Docker Environment
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/app/uploads')
app.config['OUTPUT_FOLDER'] = os.getenv('OUTPUT_FOLDER', '/app/outputs')
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024 

# The Format Matrix
IMAGE_FORMATS = {'png', 'jpg', 'bmp', 'tiff'}
VIDEO_FORMATS = {'mp4', 'mov', 'avi'}
PACKAGE_FORMATS = {'deb', 'tgz', 'rpm'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash("No file part detected.", "error")
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    target_ext = request.form.get('target_format')

    # Tagging the file for the worker
    tagged_filename = f"{file.filename}.target.{target_ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], tagged_filename)
    file.save(save_path)

    # Predict final filename for the token
    base, _ = os.path.splitext(file.filename)
    if target_ext in IMAGE_FORMATS:
        output_filename = f"{base}_converted.{target_ext}"
    else:
        output_filename = f"{base}.{target_ext}"
    
    token = base64.urlsafe_b64encode(output_filename.encode()).decode().strip("=")
    status_url = url_for('check_status', token=token)

    size_mb = os.path.getsize(save_path) // (1024 * 1024)
    if size_mb > 100:
        message = Markup(f'High load! Size: {size_mb}MB. <a href="{status_url}">Check status here</a>')
        flash(message, "warning")
    else:
        message = Markup(f'Success! Payload delivered. <a href="{status_url}">Track conversion here</a>')
        flash(message, "success")
        
    return redirect(url_for('index'))

@app.route('/status/<token>')
def check_status(token):
    try:
        # Decode token
        missing_padding = len(token) % 4
        if missing_padding:
            token += '=' * (4 - missing_padding)
        filename = base64.urlsafe_b64decode(token).decode()
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)

        is_done = os.path.exists(file_path)

        status_header = "> STATUS: DONE" if is_done else "> STATUS: Conversion in progress..."
        flash_class = "success" if is_done else "warning"
        refresh_script = f'<script>setTimeout(function(){{ location.reload(); }}, 5000);</script>' if not is_done else ''
        
        download_btn = ""
        home_link = ""
        
        if is_done:
            # Note: We use the endpoint name 'download_file' in the JS redirect
            download_btn = f'<input type="button" value="DOWNLOAD NOW" onclick="window.location.href=\'/dl/{token}\'" style="width:100%; padding:12px; background:#0e639c; color:white; border:none; font-weight:bold; cursor:pointer; margin-bottom:10px;">'
            home_link = f'<p style="margin-top: 20px;"><a href="{url_for("index")}" style="color: #4ec9b0; text-decoration: none;">[ ← RETURN TO TERMINAL ]</a></p>'

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Transformo // Status</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>> ./transformo_status</h1></div>
                <div class="flash {flash_class}">{status_header}</div>
                <div style="font-size: 0.9rem; margin-bottom: 1.5rem; border: 1px dashed #3e3e42; padding: 15px; background: #1e1e1e;">
                    <p style="color: #4ec9b0; margin-top: 0;">[ FILE_INFO ]</p>
                    <p style="margin: 5px 0;">TARGET: {filename}</p>
                    {"<p style='color: #4ec9b0;'>+ Ready for delivery.</p>" if is_done else "<p style='opacity: 0.7;'>+ Polling worker node...</p>"}
                </div>
                {download_btn}
                {home_link}
                <div class="footer">{ "Task complete." if is_done else "Auto-refreshing every 5s. Please wait." }</div>
            </div>
            {refresh_script}
        </body>
        </html>
        """
    except Exception as e:
        return redirect(url_for('index'))

# --- THIS IS THE MISSING PIECE ---
@app.route('/dl/<token>')
def download_file(token):
    try:
        missing_padding = len(token) % 4
        if missing_padding:
            token += '=' * (4 - missing_padding)
        filename = base64.urlsafe_b64decode(token).decode()
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
    except Exception:
        flash("Download failed.", "error")
        return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash("File too large! Max limit is 250MB.", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)