/**
 * content.js — edit all site text here
 *
 * This is the only file you need to touch to change words on the site.
 * After editing, just commit and push — GitHub Pages updates automatically.
 *
 * To add a new page to the home grid, add an entry to SITE.pages below,
 * create a folder (e.g. /newpage/), and drop an index.html in it.
 */

const SITE = {

  // ── Global ────────────────────────────────────────────────────────────────
  name:    "mutadatum",
  tagline: "data for the curious",

  // ── Home page ─────────────────────────────────────────────────────────────
  home: {
    eyebrow:  "Data · Film · Culture",
    headline: "Patterns hiding in plain sight",
    lede:     "mutadatum finds unexpected correlations in everyday data. Each page is one question, one dataset, one answer — or the unsettling absence of one.",
  },

  // ── Footer ────────────────────────────────────────────────────────────────
  footer: {
    left:  "© mutadatum — data journalism for the curious",
    right: "Built with TMDB &amp; DoesTheDogDie.com",
  },

  // ── Pages (shown as cards on the home page) ───────────────────────────────
  // To add a new page: copy one entry, change the fields, add your folder + HTML.
  // 'status' can be "live", "coming-soon", or "hidden" (hidden = not shown on home)
  pages: [
    {
      slug:        "dtdd",                // folder name — also becomes the URL path
      status:      "live",
      eyebrow:     "Film · Box Office · Animal Welfare",
      title:       "Does killing the dog kill the box office?",
      description: "A look at whether films where a dog dies perform differently at the box office than those where the dog makes it out alive.",
      // Preview chart config — the home card renders a tiny version of this data
      preview: {
        dataFile:  "/data/movies.json",   // path to the JSON from repo root
        xKey:      "revenue",
        yKey:      "dog_dies_pct",
        colorKey:  "dog_dies_pct",        // field used to colour points
        colorThresholds: { yes: 70, no: 30 },
        colors:    { yes: "#c0392b", no: "#2980b9", maybe: "#8e7bb5" },
      },
    },

    // Example of a coming-soon card — fill in when you're ready
    // {
    //   slug:        "oscars",
    //   status:      "coming-soon",
    //   eyebrow:     "Film · Awards",
    //   title:       "Do sad films win Oscars?",
    //   description: "Correlating IMDb emotional tone scores with Academy Award wins.",
    //   preview:     null,
    // },
  ],

};
