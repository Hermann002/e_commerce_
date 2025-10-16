FROM services-base AS web

WORKDIR /app

COPY . .

RUN chmod +x /app/script.sh

EXPOSE 8000

CMD ["sh", "script.sh"]