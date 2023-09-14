FROM gorialis/discord.py

COPY requirements.txt ./
RUN pip install -U -r requirements.txt

# Install project dependencies
WORKDIR /src

# Copy the source code in last to optimize rebuilding the image
COPY . .

CMD ["python", "-u", "./src/index.py"]