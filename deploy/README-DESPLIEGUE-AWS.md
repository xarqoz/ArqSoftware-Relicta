# Guía de Despliegue en AWS Academy (EC2)

Guía paso a paso para desplegar el ecosistema completo (Django + Flask + Nginx +
Redis + Celery) en una instancia EC2 de AWS Academy.

---

## Paso 0 — Requisitos

- Acceso a **AWS Academy Learner Lab** (o cuenta AWS).
- El repositorio en GitHub (rama `main` con la Entrega 2).

---

## Paso 1 — Iniciar el Learner Lab y lanzar la instancia EC2

1. Entra a **AWS Academy → Learner Lab → Start Lab**. Espera a que el círculo
   junto a "AWS" se ponga **verde**.
2. Haz clic en **AWS** (arriba) para abrir la consola de AWS.
3. Ve al servicio **EC2 → Instances → Launch instances**.
4. Configura:
   - **Name:** `relicta-entrega2`
   - **AMI:** *Amazon Linux 2023* (gratis, recomendada).
   - **Instance type:** `t2.medium` o `t3.medium` (2 vCPU / 4 GB — necesario
     porque levantamos 5 contenedores). `t2.micro` puede quedarse corto.
   - **Key pair:** crea uno nuevo (`relicta-key`) y **descarga el `.pem`**.
     Guárdalo bien; lo necesitas para conectarte por SSH.
   - **Network settings → Edit:** más abajo configuramos el Security Group.
5. **Storage:** sube a **20 GB** (las imágenes Docker ocupan espacio).

> ⚠️ En AWS Academy **no uses** instancias grandes (hay límite de créditos).
> `t3.medium` es el punto justo.

---

## Paso 2 — Configurar el Security Group (puertos)

En *Network settings* (al lanzar) o después en **Security Groups**, agrega estas
reglas de entrada (**Inbound rules**):

| Tipo | Protocolo | Puerto | Origen | Para qué |
|------|-----------|--------|--------|----------|
| SSH | TCP | 22 | Mi IP | Conectarte por consola |
| Custom TCP | TCP | **8080** | 0.0.0.0/0 | Acceso a la app (Nginx) |

> Solo necesitas abrir el **8080** (el puerto del API Gateway). Los demás
> servicios (Django 8000, Flask 5000, Redis 6379) son internos de Docker y
> **no** deben exponerse.

---

## Paso 3 — Asignar una IP Elástica (IP fija)

Para que la IP no cambie al reiniciar la instancia:

1. **EC2 → Elastic IPs → Allocate Elastic IP address → Allocate**.
2. Selecciona la IP creada → **Actions → Associate Elastic IP address**.
3. Asóciala a tu instancia `relicta-entrega2`.
4. Anota esa **IP elástica** (ej. `54.210.XX.XX`). Es la que entregarás.

---

## Paso 4 — Conectarte por SSH

Desde tu Mac, en la carpeta donde está el `.pem`:

```bash
chmod 400 relicta-key.pem
ssh -i relicta-key.pem ec2-user@<IP_ELASTICA>
```

> Usuario: `ec2-user` en Amazon Linux. En Ubuntu sería `ubuntu`.

---

## Paso 5 — Instalar Docker y clonar el repo

Ya dentro de la instancia:

```bash
# Clonar el proyecto
git clone https://github.com/xarqoz/ArqSoftware-Relicta.git
cd ArqSoftware-Relicta

# Instalar Docker + Compose (script incluido)
chmod +x deploy/setup-ec2.sh
./deploy/setup-ec2.sh
```

Cuando termine, **cierra la sesión SSH y vuelve a entrar** (para que el grupo
`docker` tome efecto):

```bash
exit
ssh -i relicta-key.pem ec2-user@<IP_ELASTICA>
cd ArqSoftware-Relicta
```

---

## Paso 6 — Levantar el stack

```bash
chmod +x deploy/run.sh
./deploy/run.sh
```

El script detecta la IP pública automáticamente, genera el `.env` con la
configuración correcta (CSRF, ALLOWED_HOSTS) y levanta todos los contenedores.

---

## Paso 7 — Verificar

```bash
# Estado de los contenedores (deben estar "Up")
docker compose ps

# Logs en vivo
docker compose logs -f
```

Desde tu navegador (en tu Mac):

```
http://<IP_ELASTICA>:8080/
```

Prueba también los endpoints:

```bash
curl http://<IP_ELASTICA>:8080/api/v1/info/
curl http://<IP_ELASTICA>:8080/api/v2/pagos/health
curl "http://<IP_ELASTICA>:8080/api/v1/conversion/?monto=100&origen=USD&destino=COP"
```

---

## Paso 8 — Crear el usuario administrador

```bash
docker compose exec django_web python manage.py createsuperuser
```

Luego entra a `http://<IP_ELASTICA>:8080/admin/`.

---

## Comandos útiles

```bash
docker compose ps                 # estado
docker compose logs -f django_web # logs de un servicio
docker compose restart            # reiniciar todo
docker compose down               # detener y borrar contenedores
docker compose up --build -d      # reconstruir y levantar
git pull && docker compose up --build -d   # actualizar desde GitHub
```

---

## Solución de problemas

| Síntoma | Causa / Solución |
|---------|------------------|
| No carga la página | ¿Abriste el puerto 8080 en el Security Group? ¿`docker compose ps` muestra todo "Up"? |
| `502 Bad Gateway` | Django aún arrancando; espera 30s y mira `docker compose logs django_web` |
| `CSRF verification failed` | La IP del `.env` no coincide con la que usas; re-ejecuta `./deploy/run.sh` |
| `permission denied` en docker | No reiniciaste la sesión SSH tras `setup-ec2.sh`. Sal y vuelve a entrar |
| Sin memoria / se cae | Usa `t3.medium` (4 GB), no `t2.micro` |
| La IP cambió | Asocia una **IP elástica** (Paso 3) |

---

## Para la sustentación

- ✅ La instancia EC2 debe estar **encendida** durante la sustentación.
- ✅ Entrega: **URL del repo (rama main)** + **IP elástica** (`http://<IP>:8080`).
- ⚠️ En AWS Academy el lab se **detiene** al cerrar sesión; vuelve a hacer
  **Start Lab** y la instancia se reactiva (la IP elástica se conserva).
