# Save the date: one detailed calendar and share widget per day
import json, html as _h
from urllib.parse import quote

SD_ADDR = "Banking Hall, 14 Cornhill, London EC3V 3ND"
SD_TUBE = [("Bank", "Central, Northern, Waterloo and City lines and the DLR", "about 2 minutes on foot"),
           ("Monument", "District and Circle lines", "about 5 minutes on foot"),
           ("Liverpool Street", "Elizabeth line and mainline trains", "about 10 minutes on foot")]
SD = {
 "gala": {"title": "Ghana at 70 UK: The Royal Jubilee Gala", "short": "The Royal Jubilee Gala", "page": "royal-gala",
   "dow": "Friday", "d": "5", "m": "March", "y": "2027", "s": "20270305T183000Z", "e": "20270306T003000Z",
   "iso_s": "2027-03-05T18:30:00Z", "iso_e": "2027-03-06T00:30:00Z", "hours": "18:30 to 00:30",
   "dress": "Black Tie, ball gown or Kente", "dress_more": "Kente, gold and black tie. Queens: Kente kaba and slit or an evening gown. Kings: full Kente worn toga style, or black tie with Kente.",
   "run": [("18:30", "Doors and red carpet"), ("19:45", "Last entry. The drums begin"), ("20:00", "Seated for dinner"), ("23:30", "Dancing ends"), ("00:00", "The midnight toast, as Independence Day begins"), ("00:30", "Venue closes")],
   "know": ["Doors close at 19:45, so arrive early and enjoy the red carpet", "No alcohol is included in the ticket. Bar for over 18s, Challenge 25"],
   "share": "I am going to the Royal Jubilee Gala for Ghana at 70 UK. Friday 5 March 2027, Banking Hall, City of London. Dress: Black Tie, ball gown or Kente. Come with me"},
 "ghanaday": {"title": "Ghana at 70 UK: Ghana Day Festival", "short": "Ghana Day Festival", "page": "ghana-day",
   "dow": "Saturday", "d": "6", "m": "March", "y": "2027", "s": "20270306T110000Z", "e": "20270306T180000Z",
   "iso_s": "2027-03-06T11:00:00Z", "iso_e": "2027-03-06T18:00:00Z", "hours": "11:00 to 18:00",
   "dress": "Print and denim", "dress_more": "Relaxed and ready to dance. A print top or shirt with jeans, Ankara, or your Black Stars shirt. Flat shoes or clean trainers. Full Kente cloth is for Friday.",
   "run": [("11:00", "Doors open. DJ and dancing all day"), ("12:00", "The anniversary moment"), ("16:30", "Last entry"), ("18:00", "Doors close")],
   "know": ["Seventy years to the day: Independence Day", "Keep your wristband on, and come and go as you please", "All ages welcome, children with an adult. No pushchairs or buggies. Card only bar for over 18s, Challenge 25"],
   "share": "Ghana turns 70 on Saturday 6 March 2027 and I am celebrating at the Ghana Day Festival, Banking Hall, City of London. DJ, dancing and forty Ghanaian stands. Come with me"},
 "sunday": {"title": "Ghana at 70 UK: Women of the Motherland", "short": "Women of the Motherland", "page": "women-of-the-motherland",
   "dow": "Sunday", "d": "7", "m": "March", "y": "2027", "s": "20270307T110000Z", "e": "20270307T183000Z",
   "iso_s": "2027-03-07T11:00:00Z", "iso_e": "2027-03-07T18:30:00Z", "hours": "11:00 to 18:30",
   "dress": "Sunday best", "dress_more": "Straight from church. Lace or print, a duku headwrap, gold and beads. Families in toning colours.",
   "run": [("11:00", "Doors open"), ("12:00", "The Market and the portrait studio"), ("13:00", "Afternoon tea is served"), ("14:00", "The Wall of Mothers"), ("16:00", "Networking hour"), ("18:30", "Close")],
   "know": ["Every mother honoured is named aloud at 14:00", "All ages welcome. Under 18s with an adult", "No high chairs, pushchairs or buggies"],
   "share": "I am taking my mother to Women of the Motherland, a Mothering Sunday tea for every woman of African heritage. Mothering Sunday, 7 March 2027, Banking Hall, City of London. Afternoon tea and her name on the Wall of Mothers. Join us"},
}

def sd_text(k, site, phone):
    v = SD[k]
    L = [v["title"].upper(), f'{v["dow"]} {v["d"]} {v["m"]} {v["y"]} · {v["hours"]}', "",
         "TIMINGS"] + [f"{t}  {x}" for t, x in v["run"]] + ["",
         "DRESS CODE", f'{v["dress"]}. {v["dress_more"]}', "",
         "VENUE", SD_ADDR, "",
         "NEAREST TUBE"] + [f"{a}: {b}, {c}" for a, b, c in SD_TUBE] + [
         "There is very little parking in the City. Come by Tube, train or taxi.", "",
         "BRING", "Your golden ticket QR code on your phone, and photo ID.", "",
         "GOOD TO KNOW"] + v["know"] + [
         "The venue is on two floors connected by stairs only.", "",
         f"Questions: call Asantewaa on {phone}", f'{site}/{v["page"]}']
    return "\n".join(L)

def sd_links(k, site, phone):
    v = SD[k]; body = sd_text(k, site, phone)
    g = ("https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + quote(v["title"]) + "&dates=" + v["s"] + "/" + v["e"]
         + "&details=" + quote(body) + "&location=" + quote(SD_ADDR) + "&ctz=Europe/London")
    o = lambda host: (f"https://{host}/calendar/0/action/compose?subject=" + quote(v["title"]) + "&startdt=" + v["iso_s"] + "&enddt=" + v["iso_e"]
                      + "&body=" + quote(body) + "&location=" + quote(SD_ADDR) + "&path=%2Fcalendar%2Faction%2Fcompose&rru=addevent")
    return g, o("outlook.live.com"), o("outlook.office.com"), body

def save_date(k, site, phone, band="ivory", sid="save-date", hidden=False, head=True):
    v = SD[k]; g, ol, o365, body = sd_links(k, site, phone)
    data = {"k": k, "title": v["title"], "s": v["s"], "e": v["e"], "loc": SD_ADDR, "body": body, "url": f'{site}/{v["page"]}', "share": v["share"]}
    run = "".join(f"<li><time datetime=\"{t}\">{t}</time><span>{x}</span></li>" for t, x in v["run"])
    tube = "".join(f"<li><b>{a}</b><span>{b}</span><em>{c}</em></li>" for a, b, c in SD_TUBE)
    know = "".join(f"<li>{x}</li>" for x in v["know"])
    e = _h.escape
    return f'''<section class="band {band} sd" id="{sid}"{" hidden" if hidden else ""} data-sd='{e(json.dumps(data), quote=True)}'><div class="wrap">
  {'<div class="section-head center"><span class="eyebrow">Save the date</span><h2>Put it in your diary now.</h2><p class="lead">Everything you need on the day, saved to your calendar in one tap: timings, dress code, the nearest Tube and what to bring.</p></div>' if head else ''}
  <div class="sd-grid">
    <article class="sd-card">
      <div class="sd-top">
        <div class="sd-tile" aria-hidden="true"><span>{v["dow"][:3]}</span><b>{v["d"]}</b><span>{v["m"][:3]} {v["y"]}</span></div>
        <div class="sd-name"><span class="eyebrow">{v["dow"]} {v["d"]} {v["m"]} {v["y"]}</span><h3>{v["short"]}</h3><p>{v["hours"]} · {SD_ADDR}</p></div>
      </div>
      <div class="sd-cols">
        <div class="sd-block"><h4 class="sd-h">Timings</h4><ol class="sd-run">{run}</ol></div>
        <div class="sd-block"><h4 class="sd-h">Dress code</h4><p class="sd-dress"><b>{v["dress"]}.</b> {v["dress_more"]}</p>
          <h4 class="sd-h">Bring</h4><p>Your golden ticket QR code on your phone, and photo ID.</p></div>
      </div>
      <div class="sd-block"><h4 class="sd-h">Nearest Tube</h4><ul class="sd-tube">{tube}</ul><p class="sd-small">Very little parking in the City. Come by Tube, train or taxi. <a href="https://tfl.gov.uk/plan-a-journey/" target="_blank" rel="noopener">Plan your journey with TfL</a></p></div>
      <div class="sd-block"><h4 class="sd-h">Good to know</h4><ul class="sd-know">{know}<li>Two floors, connected by stairs only</li></ul></div>
    </article>
    <aside class="sd-act" aria-label="Save and share">
      <h3 class="sd-ah">Save it. Share it.</h3>
      <p class="sd-small">Every detail on this card, with a reminder the day before.</p>
      <div class="sd-one">
        <a class="sd-btn wa" href="cal/{ {"gala": "royal-jubilee-gala", "ghanaday": "ghana-day-festival", "sunday": "women-of-the-motherland"}[k] }.ics" data-sd-ics>Add to my calendar</a>
        <button class="sd-btn" type="button" data-sd-share>Share the invitation</button>
      </div>
      <p class="sd-small sd-g">Use Google Calendar? <a href="{e(g)}" target="_blank" rel="noopener">Add it there</a></p>
      <textarea id="sd-msg-{k}" class="sd-msg" rows="4" readonly data-sd-msg hidden aria-label="Your invitation"></textarea>
      <p class="sd-ok" role="status" aria-live="polite" data-sd-ok></p>
    </aside>
  </div>
</div></section>
'''

def sd_ics(k, site, phone):
    v = SD[k]; body = sd_text(k, site, phone)
    esc = lambda t: t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    def fold(line):
        out, b = [], line.encode("utf-8")
        while len(b) > 74:
            cut = 74
            while (b[cut] & 0xC0) == 0x80: cut -= 1
            out.append(b[:cut].decode("utf-8")); b = b[cut:]
        out.append(b.decode("utf-8"))
        return "\r\n ".join(out)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Ghana at 70 UK//Save the date//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             "BEGIN:VEVENT", f"UID:{k}-2027@ghanaat70", "DTSTAMP:20261116T120000Z", f"DTSTART:{v['s']}", f"DTEND:{v['e']}",
             "SUMMARY:" + esc(v["title"]), "LOCATION:" + esc(SD_ADDR), "DESCRIPTION:" + esc(body), f"URL:{site}/{v['page']}",
             "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:" + esc(v["title"] + " is tomorrow. Dress: " + v["dress"]), "TRIGGER:-P1D", "END:VALARM",
             "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:" + esc(v["title"] + ". Nearest Tube: Bank"), "TRIGGER:-PT2H", "END:VALARM",
             "END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(fold(l) for l in lines) + "\r\n"
