<div align="center">

[![Resume Matcher](assets/header.png)](https://www.resumematcher.fyi)

# Resume Matcher

[English](README.md) | **Español** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

### *Un fork multi-tenant de [Resume Matcher](https://github.com/srbhr/Resume-Matcher)*

[𝙶𝚒𝚝𝙷𝚞𝚋](https://github.com/icemc/Resume-Matcher) ✦ [𝙳𝚘𝚌𝚔𝚎𝚛 𝙷𝚞𝚋](https://hub.docker.com/r/abanda/resume-matcher) ✦ [𝙲ó𝚖𝚘 𝚒𝚗𝚜𝚝𝚊𝚕𝚊𝚛](#how-to-install) ✦ [𝙸𝚜𝚜𝚞𝚎𝚜](https://github.com/icemc/Resume-Matcher/issues) ✦ [𝙿𝚛𝚘𝚢𝚎𝚌𝚝𝚘 𝙾𝚛𝚒𝚐𝚒𝚗𝚊𝚕](#original-project--attribution)

Crea currículums personalizados para cada postulación con sugerencias impulsadas por IA. Funciona localmente con Ollama o conéctate a tu proveedor de LLM favorito vía API.

![Resume Matcher Demo](assets/Resume_Matcher_Demo_2.gif)

*(flujo principal de adaptación de currículums, heredado del proyecto original)*

</div>

<br>

<div align="center">

![Stars](https://img.shields.io/github/stars/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8)
![Apache 2.0](https://img.shields.io/github/license/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8) ![Forks](https://img.shields.io/github/forks/icemc/Resume-Matcher?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8) ![version](https://img.shields.io/badge/Version-1.2.1--RC1-FFF?labelColor=F0F0E8&style=for-the-badge&color=1d4ed8)

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-abanda%2Fresume--matcher-FFF?labelColor=F0F0E8&logo=docker&style=for-the-badge&color=1d4ed8)](https://hub.docker.com/r/abanda/resume-matcher)

</div>

> \[!IMPORTANT]
>
> **Este es un fork independiente.** El producto principal de Resume Matcher — el constructor de currículums, la adaptación con IA, las cartas de presentación, la puntuación y las plantillas — fue diseñado y construido por **[Saurabh Rai](https://github.com/srbhr)** y la comunidad de [Resume Matcher original](https://github.com/srbhr/Resume-Matcher). Este fork existe para añadir una **arquitectura multi-tenant basada en idiomas** sobre ese trabajo (ver [Novedades de este fork](#novedades-de-este-fork) más abajo). No está afiliado, respaldado ni mantenido por el equipo original.
>
> Para el **sitio web oficial, actualizaciones, la comunidad de Discord y patrocinios**, visita el proyecto original — ver [Proyecto Original y Atribución](#original-project--attribution).

## Novedades de este fork

Cada idioma compatible es ahora su propio **tenant** — un espacio de trabajo totalmente aislado con su propia URL, su propio currículum maestro, sus propios currículums adaptados y su propio tablero de Seguimiento de Postulaciones. Nada se comparte entre tenants, excepto un único ajuste global de idioma de interfaz.

| `/en/dashboard` | `/fr/dashboard` |
|---|---|
| ![Panel en inglés](assets/en-multi-tenant.png) | ![Panel en francés](assets/fr-multi-tenant.png) |

- **Paneles por idioma** en su propia URL (`/en/dashboard`, `/fr/dashboard`, `/es/dashboard`, ...) para cada idioma compatible (inglés, español, chino, japonés, portugués, **francés** — nuevo en este fork).
- **Paridad total de funciones por tenant** — gestión de CV, adaptación, cartas de presentación, mensajes de contacto, mejora con IA y el seguimiento de postulaciones funcionan de forma independiente dentro del espacio de cada idioma.
- **Un selector de tenant** en la barra superior muestra qué idiomas ya están configurados (tienen un currículum maestro) frente a los que aún no, y te permite cambiar entre ellos con un clic.
- **El idioma de la interfaz sigue siendo global** — el idioma de la interfaz (botones, etiquetas, navegación) es un único ajuste compartido entre todos los tenants, independiente del tenant/idioma de contenido en el que estés trabajando.
- El backend aplica el aislamiento de tenants a nivel de datos: un currículum maestro por idioma (no uno global), y cada endpoint de listado/creación/carga requiere un tenant explícito.

Detalle técnico completo: [`docs/plans/language-tenant-dashboards.md`](docs/plans/language-tenant-dashboards.md).

## Primeros pasos

Resume Matcher funciona creando un currículum maestro que puedes usar para adaptar cada postulación. Instrucciones de instalación aquí: [Cómo instalar](#how-to-install)

### Cómo funciona

1. **Sube** tu currículum maestro (PDF o DOCX)
2. **Pega** la descripción del puesto al que apuntas
3. **Revisa** mejoras y contenido adaptado generado por IA
4. **Genera** carta de presentación para la postulación
5. **Personaliza** el diseño y las secciones a tu estilo
6. **Exporta** como PDF profesional con tu plantilla preferida

Cada uno de estos pasos ocurre dentro del tenant de idioma en el que te encuentres — ver [Novedades de este fork](#novedades-de-este-fork).

![Star Resume Matcher](assets/star_resume_matcher.png)

Dale una estrella a [este repositorio](https://github.com/icemc/Resume-Matcher) para apoyar el fork y recibir notificaciones de nuevas versiones.

## Funciones clave

![resume_matcher_features](assets/features.png)

### Funciones principales

**Currículum maestro**: crea un currículum maestro completo a partir de tu currículum actual.

![Job Description Input](assets/step_2.png)

### Constructor de currículum

![Resume Builder](assets/step_5.png)

Pega una descripción del puesto y obtén un currículum adaptado con ayuda de IA.

Puedes:

- Modificar el contenido sugerido
- Añadir/quitar secciones
- Reordenar secciones con arrastrar y soltar
- Elegir entre múltiples plantillas

### Generador de carta de presentación

Genera cartas de presentación adaptadas según la descripción del puesto y tu currículum.

![Cover Letter](assets/cover_letter_es.png)

### Puntuación del currículum y resaltado de palabras clave

Analiza tu currículum frente a la descripción del puesto con un puntaje de coincidencia, resaltado de palabras clave y sugerencias de mejora.

![Resume Scoring and Keyword Highlight](assets/keyword_highlighter.png)

### Seguimiento de postulaciones

Un tablero Kanban de 7 columnas (Guardado → Postulado → Sin respuesta → Respuesta → Entrevista → Aceptado → Rechazado) para seguir cada postulación, aislado por tenant de idioma.

### Exportación a PDF

Exporta tu currículum adaptado y tu carta de presentación en PDF.

### Plantillas

| Nombre de plantilla | Vista previa | Descripción |
|---------------------|-------------|-------------|
| **Clásica (una columna)** | ![Classic Template](assets/pdf-templates/single-column.jpg) | Diseño tradicional y limpio, adecuado para la mayoría de industrias. [Ver PDF](assets/pdf-templates/single-column.pdf) |
| **Moderna (una columna)** | ![Modern Template](assets/pdf-templates/modern-single-column.jpg) | Diseño contemporáneo enfocado en legibilidad y estética. [Ver PDF](assets/pdf-templates/modern-single-column.pdf) |
| **Clásica (dos columnas)** | ![Classic Two Column Template](assets/pdf-templates/two-column.jpg) | Estructura que separa secciones para mayor claridad. [Ver PDF](assets/pdf-templates/two-column.pdf) |
| **Moderna (dos columnas)** | ![Modern Two Column Template](assets/pdf-templates/modern-two-column.jpg) | Diseño elegante que usa dos columnas para mejor organización. [Ver PDF](assets/pdf-templates/modern-two-column.pdf) |

### Internacionalización

- **UI multilingüe**: interfaz disponible en inglés, español, chino, japonés, portugués (Brasil) y francés — un único ajuste global compartido entre todos los tenants.
- **Contenido multilingüe por tenant**: cada tenant de idioma genera currículums y cartas de presentación en su propio idioma — ver [Novedades de este fork](#novedades-de-este-fork).

### Roadmap

Si tienes alguna sugerencia o solicitud de características para este fork, por favor [abre un issue](https://github.com/icemc/Resume-Matcher/issues).

- AI Canvas para crear contenido de currículum impactante y basado en métricas
- Generador de plantillas de email para postulaciones
- Optimización para múltiples descripciones de trabajo

<a id="how-to-install"></a>

## Cómo instalar

![Instalación](assets/how_to_install_resumematcher.png)

Para instrucciones detalladas de configuración, consulta **[SETUP.es.md](SETUP.es.md)**.

### Requisitos previos

| Herramienta | Versión | Instalación |
|------------|---------|-------------|
| Python | 3.13+ | [python.org](https://python.org) |
| Node.js | 22+ | [nodejs.org](https://nodejs.org) |
| uv | Última | [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |

### Inicio rápido

La forma más rápida (MacOS, WSL y Ubuntu):

```bash
# Clona el repositorio
git clone https://github.com/icemc/Resume-Matcher.git
cd Resume-Matcher

# Backend (Terminal 1)
cd apps/backend
cp .env.example .env        # Configura tu proveedor de IA
uv sync                      # Instala dependencias
uv run app

# Frontend (Terminal 2)
cd apps/frontend
npm install
npm run dev
```

Abre **<http://localhost:3000>** y configura tu proveedor de IA en Settings.

### Proveedores de IA compatibles

| Proveedor | Local/Nube | Notas |
|----------|------------|-------|
| **Ollama** | Local | Gratis, se ejecuta en tu máquina |
| **OpenAI** | Nube | GPT-5 Nano, GPT-4o |
| **Anthropic** | Nube | Claude Haiku 4.5 |
| **Google Gemini** | Nube | Gemini 3 Flash |
| **OpenRouter** | Nube | Acceso a múltiples modelos |
| **DeepSeek** | Nube | DeepSeek Chat |
| **OpenAI-Compatible** | Local/Nube | Cualquier servidor que exponga la API de OpenAI Chat Completions (llama.cpp, vLLM, LM Studio, NVIDIA NIM, ...) |

### Despliegue con Docker

Las imágenes de este fork se publican para `linux/amd64` y `linux/arm64` en:

- `ghcr.io/icemc/resume-matcher`
- `abanda/resume-matcher`

Se ejecuta en un único puerto público (`3000`) con la API disponible en `/api`:

```bash
docker run --name resume-matcher \
  -p 3000:3000 \
  -v resume-data:/app/backend/data \
  abanda/resume-matcher:latest
```

Se recomienda fijar una versión en producción, por ejemplo `abanda/resume-matcher:v1.2.1-RC1`.

Endpoints:

- App: <http://localhost:3000>
- Chequeo de salud de la API: <http://localhost:3000/api/v1/health>
- Documentación de la API: <http://localhost:3000/docs>

> **¿Usas Ollama con Docker?** Usa `http://host.docker.internal:11434` como URL de Ollama en lugar de `localhost`.

### Stack tecnológico

| Componente | Tecnología |
|-----------|------------|
| Backend | FastAPI, Python 3.13+, LiteLLM |
| Frontend | Next.js 16, React 19, TypeScript |
| Base de datos | SQLite (SQLAlchemy 2.0 async / aiosqlite) |
| Estilos | Tailwind CSS 4, Swiss International Style |
| PDF | Chromium headless vía Playwright |

## Únete y contribuye

![Cómo contribuir](assets/how_to_contribute.png)

¡Damos la bienvenida a las contribuciones a este fork! Ya seas un desarrollador, diseñador o simplemente alguien que quiere ayudar — abre un issue o un pull request en [este repositorio](https://github.com/icemc/Resume-Matcher).

Echa un vistazo al roadmap si te gustaría trabajar en las características planeadas. Consulta [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md) para la guía de contribución.

<a id="contributors"></a>

## Colaboradores

<a href="https://github.com/icemc/Resume-Matcher/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=icemc/Resume-Matcher" />
</a>

<br/>

<details>
  <summary><kbd>Historial de Estrellas</kbd></summary>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=icemc/resume-matcher&theme=dark&type=Date">
    <img width="100%" src="https://api.star-history.com/svg?repos=icemc/resume-matcher&theme=dark&type=Date">
  </picture>
</details>

<a id="original-project--attribution"></a>

## Proyecto Original y Atribución

Este repositorio es un fork de **[Resume Matcher](https://github.com/srbhr/Resume-Matcher)**, creado y mantenido por **Saurabh Rai** ([@srbhr](https://github.com/srbhr)) y sus colaboradores. Todo el producto principal — el análisis de currículums, la adaptación con IA, el constructor, las cartas de presentación, la puntuación y las plantillas — es su trabajo. Este fork añade la arquitectura multi-tenant por idioma sobre esa base; todo lo demás descrito arriba pertenece al proyecto original.

Aún no tenemos sitio web, Discord ni presencia social propios, así que para todo lo siguiente, visita el **proyecto original**:

| | |
|---|---|
| 🌐 Sitio web y vista previa en vivo | [resumematcher.fyi](https://resumematcher.fyi) |
| 💬 Comunidad de Discord | [dsc.gg/resume-matcher](https://dsc.gg/resume-matcher) |
| 🐦 Twitter/X | [@srbhrai](https://twitter.com/srbhrai) |
| 💼 LinkedIn | [Resume Matcher](https://www.linkedin.com/company/resume-matcher/) |
| 👤 Creador | [srbhr.com](https://srbhr.com) |

### Patrocinio

**Por favor dirige cualquier patrocinio a los creadores originales — no a este fork.** Ellos diseñaron y construyeron el producto que este fork extiende, y son quienes deberían beneficiarse de tu apoyo:

| Plataforma  | Enlace |
|-----------|--------|
| GitHub Sponsors | [github.com/sponsors/srbhr](https://github.com/sponsors/srbhr) |
| Buy Me a Coffee | [buymeacoffee.com/srbhr](https://www.buymeacoffee.com/srbhr) |

Este fork no solicita ni acepta patrocinios propios.

### Del creador original

[![srbhr](assets/creators_note.png)](https://srbhr.com)

> Gracias por visitar Resume Matcher. Si quieres conectar, colaborar o simplemente saludar, ¡no dudes en contactarme!
> ~ **Saurabh Rai** ✨

- Website: [https://srbhr.com](https://srbhr.com)
- Linkedin: [https://www.linkedin.com/in/srbhr/](https://www.linkedin.com/in/srbhr/)
- Twitter: [https://twitter.com/srbhrai](https://twitter.com/srbhrai)
- GitHub: [https://github.com/srbhr](https://github.com/srbhr)
