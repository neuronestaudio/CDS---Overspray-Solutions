# CDS · Overspray Solutions

Premium website for **Car Detailing Solutions / Overspray Solutions** - a Melbourne
owner-operated business (Andy) offering car detailing, 10H graphene ceramic coating,
paint correction and specialist non-abrasive **overspray / industrial fallout removal**.

A rebuild of the original [cardetailingsolutions.com.au](https://www.cardetailingsolutions.com.au/)
into a modern, high-end, single-page site. All photography, testimonials and business
details are the client's own, migrated from the existing site.

## Stack

Deliberately **build-free** so it runs anywhere and can't break:

- Static HTML + vanilla CSS (custom properties, grid, `clamp()` fluid type)
- Vanilla JS - `IntersectionObserver` for nav + scroll reveals (no scroll listeners),
  gallery filtering, lightbox, animated stats
- Self-hosted fonts (Space Grotesk display + Manrope body) - no external requests
- Dark automotive theme: near-black + chrome + a single red accent (`#e11d2a`)
- Fully responsive, keyboard accessible, honours `prefers-reduced-motion`

## Run locally

```bash
# any static server works, e.g.
python -m http.server 5173
# then open http://localhost:5173
```

## Structure

```
index.html            single page
css/styles.css        design system + all sections
js/main.js            interactions
assets/img/           logo, hero, service photos, showcase video
assets/gallery/       32 real project photos
assets/fonts/         self-hosted woff2
```

## Deploy

Static - drop on GitHub Pages, Netlify, Cloudflare Pages or any host.
For GitHub Pages: Settings → Pages → deploy from `main` / root.

## To finish before going live

- Wire the quote form to a real inbox (Formspree, Netlify Forms, or a mailto fallback)
- Add a proper favicon / social share image
- Confirm the overspray removal second phone number
