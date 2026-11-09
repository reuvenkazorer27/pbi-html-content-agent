# מחקר ביקוש: מה משתמשי Power BI באמת מבקשים ואין להם

תאריך בדיקה: 09/11/2026. המטרה: לבסס את שכבת הדיפרנציאציה של הספרייה על ביקוש מתועד של משתמשים, לא על הנחות מרשימת הקטלוג. לכל שורה: ראיית הביקוש המדויקת (ציטוט + תאריך + קישור), המצב מול המובנה (דף הפיצ'ר שבבעלות הפיצ'ר), היתכנות ב-HTML Content, וההחלטה.

## סוגי הראיות (וסמכותן)

1. **בקשה ישירה של משתמש** - ציטוט מ-reddit / Fabric Ideas. הראיה החזקה ביותר לביקוש.
2. **רשימת משאלות של מומחה קהילה** - Data Goblins; מתעדת בקשות חוזרות מהשטח.
3. **leaderboard של הורדות AppSource** (DataChant, snapshot 24/07/2025) - **פרוקסי בלבד**: פופולריות של ויזואלים צד-שלישי מרמזת שאנשים מחפשים משהו מעבר למובנה, אבל אינה מוכיחה שהפיצ'ר חסר במובנה ואינה מוכיחה ביקוש דווקא למקבילה ב-HTML. משמשת רק כתימוכין, תמיד לצד בדיקת סטטוס מובנה בדף הפיצ'ר.
4. **סטטוס מובנה** - נקבע רק מול דף הפיצ'ר הספציפי ב-Microsoft Learn, בתאריך הבדיקה.

## ראיות הביקוש המדויקות

### בקשות ישירות (reddit / Fabric Ideas)

- **Timeline שטוח עם markers** - u/geophizx, r/PowerBI, 03/09/2022: "Would love to see a simple timeline that sits flat and has markers that stick up / down and then elevate with description. I've been pretty disappointed with the Gantt charts". https://www.reddit.com/r/PowerBI/comments/x46215/any_custom_visual_requests/
- **Roadmaps / milestones** - u/Nicodemus888, r/PowerBI, 23/11/2023: "Trying to visualise roadmaps, GANTT charts, milestones is execrable". https://www.reddit.com/r/PowerBI/comments/18280vs/missing_or_poorly_implemented_things/
- **Bullet ועמודות מורכבות** - u/FullllyPitted, r/PowerBI, 23/03/2026: "We use Deneb for visuals that PBI can't do. Detailed stacked bar charts, dual axis bar charts, bullet, etc." https://www.reddit.com/r/PowerBI/comments/1s1lf3m/how_often_do_you_find_that_outofthebox_viz_types/
- **קלנדר מותאם** - u/Usual-Cat6451, r/PowerBI, 11/08/2023: "Can I use this to make a custom calendar?" (אותו שרשור x46215)
- **Org chart** - Epic idea רשמי שהוגש ע"י עובד Microsoft (Miguel_Myers), 07/10/2024; תגובות משתמשים: "I had requests from leadership to create our Org chart but I did not use Power BI to do it" ‏(05/12/2024), "This would be amazing, especially when looking at workforce data" ‏(28/01/2025). https://community.fabric.microsoft.com/t5/Fabric-Ideas/Epic-idea-Organization-chart/idi-p/4520633
- **Ishikawa** - u/iammarcmason, 02/09/2022: "If you can make a good ishikawa diagram it'll be the only one (that I've seen) out there" (שרשור x46215). בקשה בודדת.

### רשימת משאלות מתועדת (Data Goblins, Kurt Buhler, 04/10/2022)

https://data-goblins.com/power-bi/visual-wishlist
- "This is essential for creating commonly-requested chart types like bullet charts, dumbbell plots" (סעיף markers/overlay על עמודות).
- "This unlocks additional visualization types, including lollipop charts, dumbbell plots and bullet charts. It would be trivially easy to create good visuals that compare actuals to target."
- על מיקום תוויות: "There is no way for me to fulfill this requirement today... we are forced to explore programmatic solutions with Deneb, R or Python."
- משאלת תוויות מבוססות-מידות: ערך + דלתא באותה תווית (8.4M ⬆0.3M ⬆4%).

### פרוקסי AppSource (DataChant leaderboard, snapshot 24/07/2025)

https://github.com/DataChant/PowerBI-Visuals-AppSource - ציון פופולריות (לא ספירת הורדות גולמית), נכון לתאריך הסנאפשוט:
- Zebra BI Tables 0.998 (טבלאות variance/IBCS, מסחרי), Apex Gantt 0.958, Sankey של ChartExpo 0.988, Water Cup 0.986 (מד התקדמות), Multi Card KPIs 0.965, ZoomCharts Drill-Down Timeline 0.936, Counter Calendar 0.89 (מוסמך).
- קריאה זהירה: זה ש-Zebra BI Tables בראש אומר שיש שוק לטבלאות variance משלמים; זה לא מוכיח שהמובנה חסר (זה נבדק בנפרד) ולא שדווקא HTML הוא התשובה.

## סטטוס מובנה (דפי הפיצ'ר, נבדק 09/11/2026)

- **Gantt**: יש ויזואל **Gantt מובנה ב-Power BI, ב-preview** - דף פיצ'ר ייעודי: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-gantt - תומך משימות, משכים, התקדמות, milestones (כש-End ריק), 3 רמות קטגוריה. זה ויזואל Power BI מובנה, לא פיצ'ר Fabric צדדי. זה **לא** אותו דבר כמו timeline קל של milestones: ה-Gantt הוא מתזמן משימות כבד, והבקשות ב-reddit מדברות על strip קל עם סמנים.
- **Bullet / dumbbell / lollipop**: אין במובנה; SQLBI מראה ש-bullet מרכיבים ידנית מעמודות ("MacGyver"): https://www.sqlbi.com/articles/building-bullet-charts-in-power-bi-reports/
- **טבלאות IBCS / variance**: אין במובנה (הקטלוג + דף הטבלאות); Zebra BI ממלא בתשלום.
- **Waffle**: אין במובנה.
- **Calendar heatmap**: עקיפין מובנה - מטריצה + conditional formatting על רקע תאים: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-conditional-formatting
- **מד התקדמות**: עקיפין - Gauge מובנה / דונאט מושחת.
- **כרטיס KPI עם ספארקליין**: Card המודרני תומך reference labels ותמונות, בלי ספארקליין: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-card ; ספארקליין בטבלה/מטריצה - מובנה (preview): https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-sparklines-tables
- **Org chart**: אין במובנה; Epic idea רשמי פתוח (לעיל).

## הטבלה: ביקוש × מובנה × היתכנות × החלטה

| רכיב | ראיית ביקוש | סטטוס מובנה | היתכנות HTML Content | החלטה |
| --- | --- | --- | --- | --- |
| Bullet chart | Deneb quote (2026) + wishlist "commonly-requested" | אין | מלא, Secure (SVG סטטי) | **בספרייה** |
| Dumbbell | wishlist "commonly-requested" | אין | מלא, Secure | **בספרייה** |
| Lollipop | wishlist | אין | מלא, Secure | **בספרייה** |
| Variance/IBCS columns | פרוקסי: Zebra BI Tables 0.998 (משלמים) | אין | מלא, Secure | **בספרייה** |
| KPI trend (תווית מורכבת + ספארק) | wishlist measure-driven labels + פרוקסי Multi Card KPIs | חלקי (Card בלי ספארק) | מלא, Secure | **בספרייה** |
| Calendar heatmap | בקשה ישירה (2023) + פרוקסי Counter Calendar 0.89 | עקיפין (מטריצה+CF) | מלא, Secure | **בספרייה** |
| Radial progress / waffle | פרוקסי: Water Cup 0.986 | עקיפין (Gauge/דונאט) | מלא, Secure | **בספרייה** |
| **Milestone timeline** (strip שטוח, סמנים למעלה/למטה) | שתי בקשות ישירות (2022, 2023) | עקיפין מתהווה: Gantt מובנה ב-preview הוא מתזמן משימות, לא strip קל | מלא, Secure: תאריכים → קואורדינטות x ב-DAX, סמנים ותוויות מעל/מתחת לציר, בלי JS | **בספרייה** (`milestone-timeline`) |
| **Org strip** (היררכיה קבועה: שורש + כפיפים) | Epic רשמי של Microsoft (2024) + תגובות משתמשים | אין | מלא במתכונת הקבועה, Secure: כרטיסים ומחברים הם SVG עם קואורדינטות שמחושבות ב-DAX; layout אוטומטי לעומק דינמי כן דורש JS (Regular) | **בספרייה** (`org-strip`, שתי רמות, עד 6 כפיפים, מגבלות מתויגות) |
| Sankey / זרימות | פרוקסי: ChartExpo 0.988 | אין | לא מומש כאן: layout של זרימות מעל נתונים שרירותיים הוא בעיית layout כללית; קואורדינטות מחושבות מראש ב-DAX יכולות לכסות מקרים קבועים, ו-JS (Regular) את הכללית | **לא** - מעבר לסקופ של הספרייה כרגע |
| Ishikawa | בקשה בודדת (2022) | אין | מלא טכנית, אבל נישתי | **לא** - ביקוש חלש מדי |
| Histogram | אזכור reddit | עקיפין (binning + עמודות) | מלא | **לא** - העקיפין המובנה סביר |

## נקודות זהירות מהמחקר (מעוגנות בספרייה)

- **תחזוקה**: u/Tee_hops (24/03/2026): "We don't like to use too much that is not ootb so future folks can inherit it with ease." מסקנה: מעט רכיבים חזקים ומתועדים, לא הרבה פרימיטיביים.
- **רישוי**: u/I_Pick_D (23/03/2026): "I can never justify either the expense or trouble involved in licensing something off the market place." מסקנה: ספריית DAX להדבקה, בלי רישוי ובלי תלות חיצונית, עונה בדיוק על זה.
- **אבטחה**: כל הרכיבים עובדים במהדורת Secure המוסמכת (בלי JS, בלי משאבים חיצוניים) - עוברים ביקורת אבטחה ארגונית ונכנסים ל-export.

## שיטת העבודה לסוכן (מעוגנת גם ב-AGENTS.md)

1. ביקוש קודם: ראיה שאנשים מבקשים את הדבר (ideas, reddit, בלוגי קהילה; leaderboard רק כפרוקסי מתויג).
2. אמת מובנה: דף הפיצ'ר הספציפי ב-Microsoft Learn, לא רשימת הקטלוג; סיווג אין מובנה / עקיפין / קיים ו-HTML מוסיף קומפוזיציה; תאריך.
3. היתכנות: מול מגבלות HTML Content (Secure: בלי JS; Regular: JS). לבדוק גם את המסלול הסטטי (DAX → קואורדינטות SVG / מיקום אבסולוטי) לפני שמסיקים "דורש JS".
4. החלטה מתועדת בטבלה כאן.
