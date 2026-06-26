# Goggle generator diff

What the data-driven base produces versus the committed goggle.

- Base rules generated: **368**
- Generated-only (new from data): **74**
- Current-only, path-qualified (overlay `# path-qualified`): **444**
- Current-only, plain (overlay `# manual`): **3211**
- Conflicts (curated value kept; review): **21**
- Total preserved in overlay: **3676**

## Generated-only (additions the automation contributes)

- `$downrank=2,site=alarabiya.net`
- `$boost=2,site=aljazeera.net`
- `$discard,site=almanar.com.lb`
- `$discard,site=almayadeen.net`
- `$discard,site=atlasobscura.com`
- `$discard,site=baidu.com`
- `$discard,site=broadwayworld.com`
- `$downrank=2,site=cbn.com`
- `$discard,site=cesnur.org`
- `$discard,site=change.org`
- `$boost=2,site=csicop.org`
- `$downrank=2,site=dailynk.com`
- `$discard,site=dailysignal.com`
- `$boost=2,site=deseret.com`
- `$discard,site=deviantart.com`
- `$discard,site=dexerto.com`
- `$discard,site=dorchesterreview.ca`
- `$discard,site=eadaily.com`
- `$discard,site=epochtimes.de`
- `$downrank=2,site=euromedmonitor.org`
- `$discard,site=exposedbycmd.org`
- `$discard,site=filmaffinity.com`
- `$discard,site=findmypast.com`
- `$discard,site=freebeacon.com`
- `$discard,site=gbnews.com`
- `$boost=2,site=glaad.org`
- `$boost=2,site=go.com`
- `$discard,site=gofundme.com`
- `$discard,site=healthline.com`
- `$downrank=2,site=heremedia.com`
- `$downrank=2,site=ijr.org`
- `$discard,site=inaturalist.org`
- `$discard,site=india.com`
- `$discard,site=indiegogo.com`
- `$discard,site=instagram.com`
- `$boost=2,site=ips.org`
- `$discard,site=journal-neo.su`
- `$discard,site=kenkurson.com`
- `$discard,site=kickstarter.com`
- `$discard,site=ladbible.com`
- `$downrank=2,site=lapatilla.com`
- `$boost=2,site=lwn.net`
- `$discard,site=mailonsunday.co.uk`
- `$discard,site=martinoticias.com`
- `$discard,site=mediaresearch.org`
- `$boost=2,site=meduza.io`
- `$downrank=2,site=metalsucks.com`
- `$downrank=2,site=middleeastmonitor.com`
- `$downrank=2,site=news.cn`
- `$discard,site=newsnationnow.com`
- `$discard,site=ngo-monitor.org`
- `$boost=2,site=oko.press`
- `$downrank=2,site=people.inc`
- `$boost=2,site=poynter.org`
- `$discard,site=redventures.com`
- `$downrank=2,site=rferl.org`
- `$downrank=2,site=rhythmone.com`
- `$downrank=2,site=ria.ru`
- `$discard,site=scientificexploration.org`
- `$boost=2,site=sky.com`
- `$downrank=2,site=socialblade.com`
- `$discard,site=statista.com`
- `$discard,site=tasnimnews.com`
- `$discard,site=tass.ru`
- `$downrank=2,site=thearda.com`
- `$boost=2,site=theinsneider.com`
- `$boost=2,site=thepinknews.com`
- `$boost=2,site=theregister.com`
- `$boost=2,site=thewire.in`
- `$discard,site=tiktok.com`
- `$downrank=2,site=timesnownews.com`
- `$discard,site=vtforeignpolicy.com`
- `$discard,site=wenweipo.com`
- `$discard,site=x.com`

## Conflicts (base disagrees with the committed goggle)

| domain | base | committed |
|---|---|---|
| acclaimedmusic.net | `$discard,site=acclaimedmusic.net` | `$boost=2,site=acclaimedmusic.net` |
| allmovie.com | `$discard,site=allmovie.com` | `$boost=2,site=allmovie.com` |
| astronautix.com | `$downrank=2,site=astronautix.com` | `$boost=2,site=astronautix.com` |
| ballotpedia.org | `$boost=2,site=ballotpedia.org` | `$downrank=2,site=ballotpedia.org` |
| catholic-hierarchy.org | `$discard,site=catholic-hierarchy.org` | `$boost=2,site=catholic-hierarchy.org` |
| cnet.com | `$discard,site=cnet.com` | `$boost=2,site=cnet.com` |
| destructoid.com | `$downrank=2,site=destructoid.com` | `$boost=2,site=destructoid.com` |
| encyclopedia.com | `$downrank=2,site=encyclopedia.com` | `$boost=2,site=encyclopedia.com` |
| forbes.com | `$downrank=2,site=forbes.com` | `$discard,site=forbes.com` |
| foxnews.com | `$discard,site=foxnews.com` | `$boost=2,site=foxnews.com` |
| hopenothate.org.uk | `$boost=2,site=hopenothate.org.uk` | `$downrank=2,site=hopenothate.org.uk` |
| investopedia.com | `$discard,site=investopedia.com` | `$downrank=2,site=investopedia.com` |
| rollingstone.com | `$discard,site=rollingstone.com` | `$boost=2,site=rollingstone.com` |
| sciencebasedmedicine.org | `$downrank=2,site=sciencebasedmedicine.org` | `$boost=2,site=sciencebasedmedicine.org` |
| si.com | `$downrank=2,site=si.com` | `$boost=2,site=si.com` |
| straitstimes.com | `$boost=2,site=straitstimes.com` | `$downrank=2,site=straitstimes.com` |
| thejc.com | `$downrank=2,site=thejc.com` | `$boost=2,site=thejc.com` |
| themarysue.com | `$boost=2,site=themarysue.com` | `$downrank=2,site=themarysue.com` |
| theneedledrop.com | `$downrank=2,site=theneedledrop.com` | `$discard,site=theneedledrop.com` |
| venturebeat.com | `$downrank=2,site=venturebeat.com` | `$boost=2,site=venturebeat.com` |
| zdnet.com | `$discard,site=zdnet.com` | `$boost=2,site=zdnet.com` |

## Current-only — preserved in the overlay

Path-qualified (444) and plain (3211) rules the base cannot derive. These live in `goggle_overlay.txt`; the path-qualified set is the target for future generation.
