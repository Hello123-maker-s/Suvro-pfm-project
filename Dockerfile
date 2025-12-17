# Use Python 3.11
FROM python:3.11

# 1. Setup a non-root user (Hugging Face Requirement)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 2. Set working directory
WORKDIR $HOME/app

# 3. Install Requirements
COPY --chown=user requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 4. Copy Application Code
COPY --chown=user . .

# 5. Fix Static Files for Whitenoise
# Create the directory and make sure the user owns it
RUN mkdir -p staticfiles
RUN DATABASE_URL="sqlite:///dummy.db" SECRET_KEY="dummy-key-for-build" python manage.py collectstatic --no-input

# 6. Expose the Hugging Face Port
EXPOSE 7860

# 7. Start Command
# Using 0.0.0.0:7860 binding
CMD ["gunicorn", "personalfinancemanager.wsgi:application", "--bind", "0.0.0.0:7860"]