# -*- coding: utf-8 -*-
"""UI language for the dashboard measures. Hebrew is the authored source; LANG=en translates
display strings only. Data values and model identifiers are masked first, so DAX filters never change.
A build fails if any Hebrew is left outside the masked parts (nothing ships half-translated)."""
import re
from config import TABLE

# authored status data values (DAX filter literals) -> English display names
STATUS_EN = {"פעיל": "Active", "באפיון": "In design", "בתחזוקה שוטפת": "Maintenance", "הושלם/פרויקט חד פעמי": "Done"}

# display strings, Hebrew -> English (applied longest-first; context characters included where needed)
EN = {
    # header
    "תיק הפרויקטים": "Project Portfolio",
    "מערכות, מסכי ניהול ו-": "Systems, ",
    "מערכות, מסכי ניהול ": "Systems, ",
    " וסוכנים · מעקב לפי סטטוס, בעלים, מחלקה ומועדי יעד": " dashboards and agents · tracked by status, owner, department and due date",
    ", סוכנים": " dashboards, agents",
    "מוצגים כל הפרויקטים": "Showing all projects",
    "סינון פעיל:": "Active filter:",
    " פרויקטים בתצוגה": " projects shown",
    "נכון ל-": "As of ",
    " נבחרו": " selected",
    # KPI cards
    "סה״כ פרויקטים": "Total projects",
    "חלף מועד היעד": "Past due",
    "בתחזוקה שוטפת": "Maintenance",
    "פעילים": "Active",
    "באפיון": "In design",
    "'>ב-\"": "'>\"",
    " מחלקות · ": " departments · ",
    " בעלי פרויקטים": " owners",
    " מהתיק": " of portfolio",
    " הושלמו": " done",
    "'>עוד \"": "'>\"",
    " מגיעים למועד ב-30 יום": " more due within 30 days",
    # lifecycle + insights
    "מחזור חיי הפרויקט": "Project lifecycle",
    "כמה פרויקטים נמצאים בכל שלב, מאפיון ועד סיום": "How many projects are at each stage, from design to done",
    "תובנות": "Insights",
    " מוביל/ה ": " leads ",
    "אין בעלים בבחירה": "No owner in the selection",
    " פעילים או באפיון כבר עברו את מועד היעד": " past due (active or in design)",
    "אין פרויקטים פעילים שעברו את מועד היעד": "No active project is past its due date",
    "&#8226; ל-": "&#8226; ",
    " מהפרויקטים לא שויכה מחלקה, ול-": " have no department · ",
    " אין מועד יעד": " no due date",
    "הושלם": "Done",
    "פעיל": "Active",
    "ללא סטטוס": "No status",
    # bar lists
    "פרויקטים לפי בעלים": "Projects by owner",
    "פרויקטים לכל בעלים, לפי סטטוס": "Projects per owner, by status",
    "פרויקטים לפי מחלקה": "Projects by department",
    "המחלקה המזמינה, לפי סטטוס": "Requesting department, by status",
    ") עדיין לא שויכו למחלקה": ") not yet assigned to a department",
    "ועוד ": "and ",
    " נוספים · העבירו את העכבר לפירוט": " more · hover for details",
    "לא שויך": "Unassigned",
    # donut
    "פרויקטים לפי סוג": "Projects by type",
    "לא הוגדר": "Not set",
    # timeline
    "לוח זמנים · פרויקטים עם מועד יעד": "Timeline · projects with a due date",
    " מתוך ": " of ",
    " פרויקטים הוגדרו עם תאריכים · ציר הזמן נקרא משמאל לימין": " projects have dates · the time axis reads left to right",
    " פרויקטים עם מועד מאוחר יותר · העבירו את העכבר לפירוט": " more projects due later · hover for details",
    "חלף המועד": "Past due",
    "היום": "Today",
    "מועד יעד": "Due date",
    "אין פרויקטים עם מועד יעד בבחירה הנוכחית": "No projects with a due date in the current selection",
    # filter panel
    "הבחירה מסננת את כל הדף": "Selections filter the whole page",
    "נוספו לאחרונה": "Recently added",
    "סוג פרויקט": "Project type",
    "סינון": "Filters",
    # single words last
    "סטטוס": "Status",
    "מחלקה": "Department",
    "בעלים": "Owner",
    "סוג": "Type",
    "פרויקטים": "projects",
}

_HEB = re.compile(r"[֐-׿]")
# never translate: column/measure refs, table refs, and the status data values when used as DAX literals
_MASK = re.compile(r"\[[^\]]*\]|" + re.escape(f"'{TABLE}'") + r"|\"(?:" + "|".join(re.escape(k) for k in STATUS_EN) + r")\"")


def translate(expr, lang):
    if lang != "en":
        return expr
    masked = []

    def keep(m):
        masked.append(m.group(0))
        return f"\x00{len(masked) - 1}\x00"
    s = _MASK.sub(keep, expr)
    for he in sorted(EN, key=len, reverse=True):
        s = s.replace(he, EN[he])
    left = _HEB.findall(re.sub(r"\x00\d+\x00", "", s))
    if left:
        i = _HEB.search(re.sub(r"\x00\d+\x00", "", s)).start()
        raise AssertionError("untranslated Hebrew in EN build: ..." + re.sub(r"\x00\d+\x00", "", s)[max(0, i - 60):i + 40])
    return re.sub(r"\x00(\d+)\x00", lambda m: masked[int(m.group(1))], s)
