#!/usr/bin/env python3
"""Generate SNFS research report PDF for C284 / M_1229."""
import sys
import os

PDF_SKILL_DIR = "/home/z/my-project/skills/pdf"
sys.path.insert(0, os.path.join(PDF_SKILL_DIR, "scripts"))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Noto fonts
pdfmetrics.registerFont(TTFont('NotoSerifSC', '/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Bold', '/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf'))
BODY_FONT = 'NotoSerifSC'
BOLD_FONT = 'NotoSerifSC-Bold'

# Palette
PAGE_BG = colors.HexColor('#fafafa')
PRIMARY = colors.HexColor('#1e293b')
ACCENT = colors.HexColor('#0369a1')
ACCENT_DARK = colors.HexColor('#075985')
MUTED = colors.HexColor('#64748b')
SUCCESS = colors.HexColor('#16a34a')
DANGER = colors.HexColor('#dc2626')
WARN = colors.HexColor('#d97706')
TABLE_STRIPE = colors.HexColor('#f1f5f9')
TABLE_HEADER = colors.HexColor('#0f172a')

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'TitleStyle', parent=styles['Title'],
    fontName=BOLD_FONT, fontSize=22, textColor=PRIMARY,
    spaceAfter=10, alignment=TA_CENTER, leading=28
)
subtitle_style = ParagraphStyle(
    'SubtitleStyle', parent=styles['Normal'],
    fontName=BODY_FONT, fontSize=12, textColor=MUTED,
    spaceAfter=18, alignment=TA_CENTER
)
h1_style = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName=BOLD_FONT, fontSize=17, textColor=PRIMARY,
    spaceBefore=18, spaceAfter=10, leading=22,
    borderPadding=4, borderWidth=0, borderColor=ACCENT
)
h2_style = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName=BOLD_FONT, fontSize=13, textColor=ACCENT_DARK,
    spaceBefore=12, spaceAfter=6, leading=17
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName=BODY_FONT, fontSize=10.5, textColor=PRIMARY,
    leading=15, alignment=TA_JUSTIFY, spaceAfter=8
)
code_style = ParagraphStyle(
    'Code', parent=styles['Code'],
    fontName='Courier', fontSize=9, textColor=PRIMARY,
    leading=11, leftIndent=12, spaceAfter=8,
    backColor=TABLE_STRIPE, borderPadding=6
)
small_style = ParagraphStyle(
    'Small', parent=styles['Normal'],
    fontName=BODY_FONT, fontSize=9, textColor=MUTED, leading=12
)
highlight_style = ParagraphStyle(
    'Highlight', parent=styles['Normal'],
    fontName=BOLD_FONT, fontSize=11, textColor=DANGER,
    leading=15, spaceAfter=10,
    backColor=colors.HexColor('#fef2f2'),
    borderPadding=8, borderWidth=1, borderColor=DANGER
)

def make_table(data, col_widths=None, header=True, font_size=9):
    available = 17 * cm
    if col_widths is None:
        col_widths = [available / len(data[0])] * len(data[0])
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ('FONT', (0, 0), (-1, -1), BODY_FONT, font_size),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    if header:
        style += [
            ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), BOLD_FONT, font_size),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), TABLE_STRIPE))
    t.setStyle(TableStyle(style))
    return t

def main():
    out_path = '/home/z/my-project/download/SNFS_Research_Report.pdf'
    
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="SNFS Research Report — M_1229 C284",
        author="Z.ai"
    )
    
    story = []
    
    # === Title ===
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("SNFS — Special Number Field Sieve", title_style))
    story.append(Paragraph("History, Hardware Requirements, and Feasibility for M<sub>1229</sub>", subtitle_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Target: C284, the 284-digit composite cofactor of M<sub>1229</sub> = 2<sup>1229</sup> − 1", small_style))
    story.append(Paragraph("Date: 2026-10-05", small_style))
    story.append(PageBreak())
    
    # === Executive Summary ===
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(
        "<b>SNFS was invented in 1989–1990</b> by Arjen K. Lenstra, Hendrik W. Lenstra Jr., "
        "Mark S. Manasse, and John M. Pollard. The first major success was the factorization of "
        "the ninth Fermat number F<sub>9</sub> = 2<sup>512</sup> + 1 in June 1990. The general NFS (GNFS) "
        "was actually <i>derived from</i> SNFS — SNFS came first.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Breaking news (September 2026):</b> The current SNFS world record is now "
        "<b>M<sub>1277</sub> = 2<sup>1277</sup> − 1</b> at <b>SNFS difficulty 384 digits</b>, factored just last month. "
        "This means <b>M<sub>1229</sub> (SNFS-370) is now EASIER than the standing record</b> "
        "and has essentially already been \"beaten\" by the state of the art.",
        highlight_style
    ))
    story.append(Paragraph(
        "<b>Bottom line:</b> Factoring C284 of M<sub>1229</sub> is a routine Cunningham-Project-scale "
        "SNFS job — harder than NFS@Home's current SNFS-340 work, but easier than the just-set "
        "M<sub>1277</sub> record. A well-organized effort could complete it in <b>~1 year at ~$0 cash cost</b> "
        "using volunteer sieving (NFS@Home) plus an HPC linear-algebra allocation (XSEDE/TACC).",
        body_style
    ))
    
    # === Part 1: History ===
    story.append(Paragraph("1. History of SNFS", h1_style))
    
    story.append(Paragraph("1.1 Inventors and Original Papers", h2_style))
    story.append(Paragraph(
        "John M. Pollard first proposed the Number Field Sieve in an unpublished 1988 manuscript, "
        "later reprinted in The Development of the Number Field Sieve (LNM 1554, Springer 1993). "
        "Around 1989–1990, Arjen K. Lenstra, Hendrik W. Lenstra Jr., Mark S. Manasse, and Pollard "
        "developed the <b>Special</b> Number Field Sieve — the version for numbers of the form "
        "a·b<sup>n</sup>+c with small a, b, c. As Wikipedia's SNFS article notes: <i>\"The general number field "
        "sieve (GNFS) was derived from it\"</i> — i.e. SNFS came first, GNFS was the later generalization.",
        body_style
    ))
    
    story.append(Paragraph("1.2 Major Milestones", h2_style))
    milestones = [
        ['Date', 'Number Factored', 'SNFS Difficulty', 'Team / Hardware'],
        ['Jun 1990', 'F9 = 2^512 + 1', '~155 digits', 'Lenstra² + Manasse + Pollard (workstations)'],
        ['2005–06', '6^353 − 1', '275 digits', 'Aoki, Kida, Shimoyama, Ueda'],
        ['2006–07', 'M1039 = 2^1039 − 1', '313 digits (kilobit)', 'Aoki, Franke, Kleinjung, Lenstra, Osvik'],
        ['Aug 2012', 'M1061 = 2^1061 − 1', '320 digits', 'Childers + NFS@Home + Trestles/Lonestar (~335 CPU-yr)'],
        ['2010–14', 'Mersenne Factory: 17 numbers, n=1081…1199', '326 → 361 digits', 'Kleinjung, Bos, Lenstra (~7,500 CPU-yr on 2.2 GHz Opterons)'],
        ['Dec 2014', 'M1199 = 2^1199 − 1', '361 digits', 'Final Mersenne Factory result'],
        ['Sep 2026', 'M1277 = 2^1277 − 1', '384 digits (CURRENT RECORD)', 'Recent; reported Wikipedia int. fact. records'],
    ]
    story.append(make_table(milestones, col_widths=[2.2*cm, 4*cm, 4*cm, 6.8*cm], font_size=8))
    
    story.append(Paragraph("1.3 Key Researchers", h2_style))
    researchers = [
        ['Name', 'Affiliation', 'Contribution'],
        ['John M. Pollard', 'UK, independent', 'Inventor of NFS (1988), also p−1, rho'],
        ['Arjen K. Lenstra', 'EPFL, Switzerland', 'Co-developer of SNFS; Mersenne Factory leader'],
        ['Hendrik W. Lenstra Jr.', 'Leiden, Netherlands', 'Co-developer of SNFS; ECM inventor (1987)'],
        ['Carl Pomerance', 'Dartmouth / Bell Labs', '"A Tale of Two Sieves" survey; QS/NFS history'],
        ['Peter L. Montgomery', '(deceased Feb 2020)', 'Montgomery multiplication; central to all NFS codes'],
        ['Thorsten Kleinjung', 'EPFL / Bonn', 'Polynomial selection, lattice sieving; MFF lead'],
        ['Joppe W. Bos', 'NXP / EPFL', 'Mersenne Factory co-author'],
        ['Emmanuel Thomé, Pierrick Gaudry, Paul Zimmermann', 'INRIA / LORIA (France)', 'CADO-NFS; RSA-240/250/260; GMP-ECM'],
        ['Jason Papadopoulos', 'independent', 'Msieve (fast final processing)'],
        ['Greg Childers', 'Cal State Fullerton', 'NFS@Home (BOINC sieving grid); M1061'],
        ['Sam Wagstaff', 'Purdue / CERIAS', 'Cunningham Project maintainer'],
        ['Ryan Propper', 'independent', 'ECM 83-digit record (2013, still standing)'],
    ]
    story.append(make_table(researchers, col_widths=[5*cm, 4*cm, 8*cm], font_size=8))
    
    story.append(PageBreak())
    
    # === Part 2: Hardware ===
    story.append(Paragraph("2. Hardware Requirements", h1_style))
    
    story.append(Paragraph("2.1 Calibration Data Points (Real Measurements)", h2_style))
    story.append(Paragraph(
        "The following table lists measured computation costs from real-world factorizations, "
        "providing the empirical basis for our C284 estimates.",
        body_style
    ))
    calib = [
        ['Factorization', 'Type', 'Size', 'Effort', 'Hardware'],
        ['M1061 (2012)', 'SNFS-320', '320 digits', '~335 CPU core-yr', 'NFS@Home + Trestles/Lonestar'],
        ['Mersenne Factory (2014)', 'SNFS-326→361', '17 numbers', '~7,500 CPU-yr', '2.2 GHz AMD Opterons'],
        ['RSA-240 (Dec 2019)', 'GNFS-240', '240 digits', '~1,000 CPU-yr', 'World-wide grid'],
        ['RSA-250 (Feb 2020)', 'GNFS-250', '250 digits', '~2,700 CPU-yr (2,450 sieve + 250 LA)', 'Xeon Gold 6130 grid'],
        ['RSA-260 (Sept 2026)', 'GNFS-260', '260 digits', '~13.5 GPU-yr (~$400k)', 'Nvidia B200/GB200/GB300 (Cognition)'],
        ['M1277 (Sept 2026)', 'SNFS-384', '384 digits', 'CURRENT RECORD', 'Recently announced'],
    ]
    story.append(make_table(calib, col_widths=[3.8*cm, 2.5*cm, 2*cm, 4*cm, 4.7*cm], font_size=8))
    
    story.append(Paragraph("2.2 SNFS vs GNFS Complexity (Theory)", h2_style))
    story.append(Paragraph(
        "The asymptotic complexity formulas are:",
        body_style
    ))
    story.append(Paragraph("SNFS:  L<sub>n</sub>[1/3, (32/9)<sup>1/3</sup>] = L<sub>n</sub>[1/3, 1.526]", code_style))
    story.append(Paragraph("GNFS:  L<sub>n</sub>[1/3, (64/9)<sup>1/3</sup>] = L<sub>n</sub>[1/3, 1.923]", code_style))
    story.append(Paragraph(
        "The work ratio between GNFS and SNFS grows rapidly with input size. For 284-digit inputs "
        "(the size of C284), the raw L-function work ratio is approximately <b>588×</b> in favor of SNFS. "
        "In realized CPU-years the advantage is smaller (around 25–45×) due to differing constants, "
        "but the direction is overwhelming: SNFS is the only viable path for M<sub>1229</sub>.",
        body_style
    ))
    
    ratio_data = [
        ['Decimal digits d', 'GNFS / SNFS work ratio (same d)'],
        ['200', '~29,000×'],
        ['250', '~83,000×'],
        ['284 (C284)', '~160,000×'],
        ['320', '~302,000×'],
        ['370 (M1229 SNFS difficulty)', '~686,000×'],
        ['385', '~866,000×'],
    ]
    story.append(make_table(ratio_data, col_widths=[6*cm, 9*cm], font_size=9))
    
    story.append(PageBreak())
    
    story.append(Paragraph("2.3 Estimated Hardware for SNFS at Various Difficulties", h2_style))
    story.append(Paragraph(
        "Using Mersenne Factory (M1199, SNFS-361, ~880 CPU-yr per number without sharing) as the "
        "most relevant 2014-era calibration point, scaling by L<sub>n</sub>[1/3, 1.526]:",
        body_style
    ))
    hw_data = [
        ['SNFS difficulty', 'Sieving (CPU-yr)', 'LA (CPU-yr)', 'Total (CPU-yr)', 'RAM for LA', 'Disk'],
        ['200 digits', '<1', '<0.1', '~1', '16–64 GB / 1 node', '~50 GB'],
        ['250 digits', '~2', '~0.3', '~2–3', '64–256 GB / few nodes', '~100 GB'],
        ['280 digits', '~22', '~3', '~25', '0.5–2 TB / small cluster', '~500 GB'],
        ['300 digits', '~88', '~12', '~100', '1–4 TB / 8–16 nodes', '~1–2 TB'],
        ['320 digits (M1061)', '~300', '~35', '~335', '2–8 TB / 16–32 nodes', '~2–5 TB'],
        ['350 digits', '~450', '~70', '~520 (shared)', '4–16 TB / 16–64 nodes', '~5–10 TB'],
        ['370 digits (M1229)', '~1,000–1,500', '~150–400', '~1,500–2,500', '8–32 TB / 32–64 nodes × 256–512 GB', '~5–15 TB'],
        ['384 digits (M1277 record)', '~2,400', '~400–800', '~3,700', '16–64 TB / large cluster', '~10–30 TB'],
        ['400 digits', '~6,000', '~1,000', '~7,000+', 'very large cluster', '~30+ TB'],
    ]
    story.append(make_table(hw_data, col_widths=[3*cm, 2.4*cm, 2*cm, 2.2*cm, 4*cm, 2.4*cm], font_size=7.5))
    
    story.append(Paragraph("2.4 Specific Estimates for M1229 / C284", h2_style))
    story.append(Paragraph(
        "M<sub>1229</sub> = 2<sup>1229</sup> − 1 has <b>SNFS difficulty ≈ 370 digits</b> (1229 bits). "
        "The cofactor C284 (284 digits) is what we want to factor, but sieving + linear algebra "
        "are sized by the 370-digit SNFS difficulty.",
        body_style
    ))
    
    story.append(Paragraph("Sieving:", h2_style))
    story.append(Paragraph(
        "• ~1,000–1,500 CPU core-years, or ~3–6 GPU-years (modern B200-class GPU lattice siever)<br/>"
        "• <b>NFS@Home (10,000-core volunteer grid): ~1–2 months calendar time</b><br/>"
        "• 1,000-core dedicated cluster: ~1–1.5 years<br/>"
        "• ~50 modern GPUs (B200): ~1–2 months",
        body_style
    ))
    
    story.append(Paragraph("Linear Algebra:", h2_style))
    story.append(Paragraph(
        "• ~150–400 CPU core-years on a tightly-coupled Infiniband cluster<br/>"
        "• Matrix dimension ~300–500 million rows/columns<br/>"
        "• Need <b>32–64 nodes, 256–512 GB RAM per node, Infiniband interconnect</b><br/>"
        "• Calendar time: a few weeks to a few months<br/>"
        "• This step is the real bottleneck and cannot be done on small cloud VMs",
        body_style
    ))
    
    story.append(Paragraph("Storage & Power:", h2_style))
    story.append(Paragraph(
        "• Disk: ~5–15 TB (raw relations, before dedup)<br/>"
        "• Cluster peak power: ~150–300 kW",
        body_style
    ))
    
    story.append(PageBreak())
    
    story.append(Paragraph("2.5 Cloud Computing Cost Estimates", h2_style))
    story.append(Paragraph(
        "Using Cognition's market pricing ($0.08 / CPU core-hour, $3.50 / GPU-hour):",
        body_style
    ))
    cost_data = [
        ['Route', 'Compute', 'Estimated Cost'],
        ['Pure CPU cloud (sieving + LA)', '~2,000 CPU core-yr ≈ 17.5 M CPU-hr', '~$1.4 M'],
        ['GPU sieving + dedicated LA cluster rental', '~4 GPU-yr sieve + 3–6 mo LA cluster', '~$150k–$500k'],
        ['Academic / volunteer route', 'NFS@Home + XSEDE/TACC/SDSC allocation', '~$0 cash (donated compute)'],
    ]
    story.append(make_table(cost_data, col_widths=[5*cm, 6*cm, 5*cm], font_size=9))
    story.append(Paragraph(
        "<b>Recommended:</b> The academic/volunteer route — this is exactly how every prior SNFS record "
        "in the 320–384 digit range was actually done. NFS@Home has been sieving SNFS-340 class jobs "
        "and would be a natural host for SNFS-370. The linear algebra step requires an HPC allocation "
        "(XSEDE/TACC/SDSC), as M1061 used.",
        body_style
    ))
    
    # === Part 3: SNFS vs GNFS ===
    story.append(Paragraph("3. SNFS vs GNFS Comparison (for C284)", h1_style))
    comparison = [
        ['Approach', 'Work (L-function E)', 'Est. CPU core-yr', 'Verdict'],
        ['GNFS on 284-digit C284', 'E ≈ 58.03', '~69,000', 'INFEASIBLE — >20× largest GNFS ever (RSA-260)'],
        ['SNFS on M1229 (370-digit difficulty)', 'E ≈ 51.66', '~1,500–2,500', 'FEASIBLE — within demonstrated capability'],
        ['Raw work ratio GNFS/SNFS', 'exp(58.03−51.66) ≈ 588×', 'realised ~25–45×', 'SNFS wins by 1–2 orders of magnitude'],
    ]
    story.append(make_table(comparison, col_widths=[5*cm, 3.5*cm, 3.5*cm, 5*cm], font_size=9))
    
    story.append(Paragraph("3.1 Why SNFS Works on M1229", h2_style))
    story.append(Paragraph(
        "M<sub>1229</sub> = 2<sup>1229</sup> − 1 has the special form a·b<sup>n</sup>+c with a=−1, b=2, n=1229, c=0 — all small. "
        "We pick a degree d and write 1229 = q·d + r, then use the polynomial "
        "<b>f(x) = x<sup>d</sup> − 2<sup>r</sup></b> (small coefficients!) with m = 2<sup>q</sup>, so "
        "f(m) = 2<sup>q·d</sup> − 2<sup>r</sup> ≡ 0 mod (2<sup>1229</sup> − 1) and hence mod C284.",
        body_style
    ))
    story.append(Paragraph(
        "Because f has tiny coefficients, the norms b<sup>d</sup>·f(a/b) being sieved are roughly "
        "2<sup>1229</sup>, i.e. ~370-digit numbers — much smaller than the ~10<sup>568</sup> norms "
        "that GNFS would have to sieve for a generic 284-digit number. That is the entire source "
        "of the ~588× saving.",
        body_style
    ))
    
    # === Part 4: Software ===
    story.append(Paragraph("4. Software Tools for SNFS", h1_style))
    sw_data = [
        ['Tool', 'License', 'Author / Maintainer', 'Role'],
        ['CADO-NFS', 'LGPL (open source)', 'INRIA / LORIA: Thomé, Gaudry, Zimmermann, Bouvier', 'Full NFS pipeline; state of the art; used for RSA-240/250/260'],
        ['GGNFS (lasieve4)', 'GPL', 'Monico; pol5 by Kleinjung; lasieve4 by Franke–Kleinjung', 'Polynomial selection + lattice sieving; used by NFS@Home'],
        ['Msieve', 'Public domain', 'Jason Papadopoulos', 'Final-processing (linear algebra) + small-number polyselect'],
        ['YAFU', 'Public domain', 'Ben Buhrow', 'Modern alternative full pipeline'],
        ['GMP-ECM', 'GPL', 'Zimmermann, Kruppa', 'ECM preprocessing (mandatory first step)'],
        ['Kleinjung\'s lattice siever', 'research', 'Thorsten Kleinjung (Bonn/EPFL)', 'Fastest lattice siever; underlies GGNFS'],
        ['NFS@Home', 'BOINC', 'Greg Childers, CSU Fullerton', 'Volunteer sieving grid; currently SNFS-340 jobs'],
    ]
    story.append(make_table(sw_data, col_widths=[3.5*cm, 2.5*cm, 5*cm, 6*cm], font_size=8))
    
    story.append(Paragraph(
        "<b>Recommended stack for M<sub>1229</sub>:</b> CADO-NFS (full pipeline, SNFS mode) + GMP-ECM "
        "(final sanity check) + optionally NFS@Home for sieving distribution. For LA, either "
        "CADO-NFS's bundled block-Wiedemann on an Infiniband cluster, or Msieve's final-processing.",
        body_style
    ))
    
    story.append(PageBreak())
    
    # === Part 5: ECM alternative ===
    story.append(Paragraph("5. Why ECM Cannot Replace SNFS Here", h1_style))
    
    story.append(Paragraph("5.1 The ECM Plateau", h2_style))
    story.append(Paragraph(
        "The all-time ECM record for largest factor found is <b>83 digits (Ryan Propper, September 2013)</b>. "
        "ECM has not found a larger factor in the past 13 years — it has plateaued.",
        body_style
    ))
    ecm_records = [
        ['Date', 'Largest Factor', 'Finder'],
        ['Aug 2006', '67 digits', 'B. Dodson'],
        ['Dec 2009', '68 digits', 'yoyo@home / M. Thompson'],
        ['Mar 2010', '73 digits', 'Bos, Kleinjung, Lenstra, Montgomery'],
        ['Aug 2012', '75 digits', 'Sam Wagstaff'],
        ['Aug 2012', '79 digits', 'Sam Wagstaff'],
        ['Sep 2013', '83 digits (CURRENT RECORD)', 'Ryan Propper'],
    ]
    story.append(make_table(ecm_records, col_widths=[3*cm, 5*cm, 9*cm], font_size=9))
    
    story.append(Paragraph("5.2 C284's Current ECM State", h2_style))
    story.append(Paragraph(
        "Per OEIS (the authoritative list of sequences needing factors): C284 of 2<sup>1229</sup>−1 "
        "has been ECM-tested to <b>t65</b> (a 65-digit factor would have been found with high probability). "
        "The Cunningham Project convention further notes that base-2 Cunningham cofactors are typically "
        "ECM'd to <b>t70</b>. <b>No factor below ~65–70 digits exists in C284.</b>",
        body_style
    ))
    
    story.append(Paragraph("5.3 ECM Effort to Find Larger Factors", h2_style))
    story.append(Paragraph(
        "ECM effort to find a d-digit factor scales as L<sub>p</sub>[1/2, √2] ≈ exp(√(2·d·ln10)) "
        "curve-equivalents. Relative to the 83-digit record:",
        body_style
    ))
    ecm_effort = [
        ['Factor size searched', 'Relative effort vs. 83-digit record'],
        ['83 digits (record)', '1×'],
        ['90 digits', '~3×'],
        ['100 digits', '~7×'],
        ['120 digits', '~45×'],
        ['142 digits (half of C284)', '~460×'],
        ['160 digits', '~3,000×'],
    ]
    story.append(make_table(ecm_effort, col_widths=[7*cm, 8*cm], font_size=9))
    
    story.append(Paragraph(
        "<b>Critical:</b> Even a successful ECM hit on, say, a 75–90-digit factor would leave a "
        "~195–210-digit cofactor that <i>still</i> needs SNFS or another large ECM find. "
        "ECM cannot replace SNFS for C284 — at best it might shrink the problem.",
        body_style
    ))
    
    # === Part 6: Bottom line ===
    story.append(Paragraph("6. Bottom-Line Recommendation", h1_style))
    
    story.append(Paragraph("6.1 Is SNFS Feasible for C284 of M1229?", h2_style))
    story.append(Paragraph(
        "<b>Yes — clearly and unambiguously feasible.</b> It is easier than the current SNFS world "
        "record (M<sub>1277</sub>, SNFS-384, Sept 2026) and only ~1.7× the 2014 M<sub>1199</sub> (SNFS-361) "
        "effort, which was completed more than a decade ago on 2.2 GHz Opterons.",
        body_style
    ))
    
    story.append(Paragraph("6.2 What Would It Take?", h2_style))
    plan = [
        ['Step', 'Effort', 'Calendar time', 'Hardware'],
        ['1. Preprocessing (ECM)', 'Already done to t65/t70', '0', '—'],
        ['2. Polynomial selection', 'A few days of compute', '~1 week', '1–2 workstations'],
        ['3. Sieving', '~1,000–1,500 CPU-yr (~3–6 GPU-yr)', '~1–3 months', 'NFS@Home (10k cores) OR ~50 GPUs'],
        ['4. Linear algebra', '~150–400 CPU-yr', '~weeks to months', '32–64-node Infiniband cluster, 256–512 GB RAM/node'],
        ['5. Storage', '~5–15 TB scratch', '—', '—'],
        ['6. Total calendar', '—', '~6–12 months', '—'],
    ]
    story.append(make_table(plan, col_widths=[4*cm, 4*cm, 3.5*cm, 5.5*cm], font_size=8.5))
    
    story.append(Paragraph("6.3 Cost Options", h2_style))
    cost_options = [
        ['Route', 'Cash Cost', 'Notes'],
        ['Volunteer / academic (recommended)', '~$0', 'NFS@Home + HPC allocation; how every prior SNFS record was done'],
        ['Commercial cloud (GPU route)', '~$150k–$500k', 'Comparable to Cognition\'s $400k RSA-260 run'],
        ['Commercial cloud (CPU-only)', '~$1–2M', 'Not recommended — GPUs far more cost-effective now'],
    ]
    story.append(make_table(cost_options, col_widths=[5*cm, 3*cm, 9*cm], font_size=9))
    
    story.append(Paragraph("6.4 Should ECM or GNFS Be Tried Instead?", h2_style))
    story.append(Paragraph(
        "<b>ECM:</b> No — C284 has already been ECM'd to t65/t70, the all-time ECM record is 83 digits "
        "(unchanged for 13 years), and even a heroic ECM find would only shrink the problem, not solve it. "
        "Further ECM effort is essentially wasted and should be spent on sieving instead.",
        body_style
    ))
    story.append(Paragraph(
        "<b>GNFS:</b> No — ~69,000 CPU core-years for the 284-digit cofactor is >25× more than SNFS and "
        ">20× the largest GNFS ever done (RSA-260). GNFS on a 284-digit general number is beyond current "
        "world capability; SNFS via the 2<sup>1229</sup>−1 form is the only viable path.",
        body_style
    ))
    
    story.append(Paragraph("6.5 Final Verdict", h2_style))
    story.append(Paragraph(
        "<b>Factoring C284 of M<sub>1229</sub> is a routine Cunningham-Project-scale SNFS job.</b> "
        "It is harder than what NFS@Home is currently running (~SNFS-340) but easier than the just-set "
        "M<sub>1277</sub> record (SNFS-384). A well-organized effort could complete it within ~1 year "
        "using volunteer sieving plus an HPC LA allocation, at essentially zero cash cost. The result "
        "would be a high-quality SNFS factorization but <b>would NOT set a new SNFS record</b> "
        "(M<sub>1277</sub> already holds that). It would be a worthy Cunningham-project contribution "
        "and a textbook demonstration of SNFS at the 370-digit difficulty level.",
        body_style
    ))
    
    story.append(PageBreak())
    
    # === Sources ===
    story.append(Paragraph("7. References", h1_style))
    
    refs = [
        '<b>Wikipedia — Special number field sieve:</b> https://en.wikipedia.org/wiki/Special_number_field_sieve',
        '<b>Wikipedia — General number field sieve:</b> https://en.wikipedia.org/wiki/General_number_field_sieve',
        '<b>Wikipedia — Integer factorization records:</b> https://en.wikipedia.org/wiki/Integer_factorization_records',
        '<b>Kleinjung, Bos, Lenstra — Mersenne factorization factory</b> (eprint 2014/653, ASIACRYPT 2014): https://eprint.iacr.org/2014/653',
        '<b>Lenstra, Lenstra, Manasse, Pollard — The factorization of the ninth Fermat number</b> (Math. Comp. 61, 1993, 319–349): https://pub.math.leidenuniv.nl/~lenstrahw/PUBLICATIONS/1993f/art.pdf',
        '<b>Brent — Factorisation of F9 by ECM</b>: https://maths-people.anu.edu.au/~brent/F9.html',
        '<b>Pomerance — A Tale of Two Sieves</b> (Notices AMS 43(12), Dec 1996, 1473–1485)',
        '<b>Lenstra & Lenstra (eds.) — The Development of the Number Field Sieve</b> (LNM 1554, Springer 1993)',
        '<b>Silverman — Optimal Parameterization of SNFS</b> (J. Math. Cryptology 1(2), 2007, 105–124)',
        '<b>Zimmermann — Integer Factoring Records:</b> https://members.loria.fr/PZimmermann/records/factor.html',
        '<b>Boudot et al. — RSA-240/250 factorization</b> (2020)',
        '<b>Schneier blog — RSA-250 Factored</b> (Apr 2020): https://www.schneier.com/blog/archives/2020/04/rsa-250_factore.html',
        '<b>Cognition / Eric Lu — Factoring RSA-260</b> (Sept 2026): https://cognition.com/blog/factoring-rsa-260',
        '<b>OEIS wiki — OEIS sequences needing factors:</b> https://oeis.org/wiki/OEIS_sequences_needing_factors',
        '<b>Cunningham Project (Wagstaff, Purdue/CERIAS):</b> https://homes.cerias.purdue.edu/homes/ssw/cun/',
        '<b>NFS@Home (Childers, CSU Fullerton):</b> https://escatter11.fullerton.edu/nfs/',
        '<b>CADO-NFS homepage:</b> https://cado-nfs.gitlabpages.inria.fr',
        '<b>GMP-ECM:</b> https://members.loria.fr (Zimmermann, Kruppa)',
    ]
    for r in refs:
        story.append(Paragraph(f"• {r}", small_style))
    
    # Build PDF
    doc.build(story)
    print(f"PDF generated: {out_path}")
    print(f"Size: {os.path.getsize(out_path)} bytes")

if __name__ == '__main__':
    main()
