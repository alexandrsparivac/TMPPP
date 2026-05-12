# Imagine de baza oficiala Python
FROM python:3.10-slim

# Prevenirea generarii fisierelor .pyc si asigurarea afisarii log-urilor in timp real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Seteaza directorul de lucru in container
WORKDIR /app

# Instaleaza dependentele sistem necesare (daca e cazul)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiaza fisierul de dependente si le instaleaza
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiaza intregul proiect in container
COPY . .

# Creeaza directorul pentru log-uri (daca nu exista)
RUN mkdir -p logs

# Comanda de pornire a botului
# Nota: Se foloseste modulul student_life_helper cu argumentul telegram
CMD ["python", "-m", "student_life_helper", "telegram"]
