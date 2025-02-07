![logo@2x](https://github.com/user-attachments/assets/d1f264a2-9ead-42f5-81a0-8ce67418591a)

# Scomet: Administrăm confortul - Integrare pentru Home Assistant!
Această integrare oferă monitorizare completă a datelor contractuale disponibile pentru utilizatorii Scomet. Integrarea se poate configura prin interfața UI și permite afișarea diferitelor date disponibile în contul de utilizator. 🚀

# 🌟 Caracteristicile butoanelor
**Push button `Plătește acum`**
  - Deschide pagina de plată a facturii. Pentru ca acesta să funcționeze aveți nevoie ca browser mod să fie instalat.

# 🌟 Caracteristicile senzorilor
**Senzorul `Consum Apă Rece`**
  - Afișează consumul de apă rece din ultima lună.

**Senzorul `Dată emitere factură`**
  - Afișează data de emitere a ultimei facturi.

**Senzorii `Dată scadentă factură`**
  - Afișează data scadentă a ultimei facturi.

**Senzorul `Număr Persoane`**
  - Afișează numărul de persoane declarat.

**Senzorul `Sold`**
  - Afișează soldul de la ultima factură.

**Senzorul `Total`**
  - Afișează totalul de plată din ultima factură.

# ⚙️Configurare

**🛠️Interfața UI**
1. Adaugă integrarea din meniul **Setări > Dispozitive și Servicii > Adaugă Integrare.**
2. Introdu datele contului Scomet:
     - **email:** email-ul folosit pentru logarea în contul Scomet
     - **password:** parola contului Scomet

# 🚀Instalare
**💡 Instalare prin HACS:**
1. Adaugă [depozitul personalizat](https://github.com/geotibi/scomet) în HACS.🛠️
2. Caută integrarea "Scomet: Administrăm confortul" și instaleaz-o. ✅
3. Repornește Home Assistant și configurează integrarea. 🔄

**✋ Instalare manuală:**
1. Clonează sau descarcă [depozitul GitHub](https://github.com/geotibi/scomet). 📂
2. Copiază folderul custom_components/scomet în directorul custom_components al Home Assistant. 🗂️
3. Repornește Home Assistant și configurează integrarea. 🔄

# ✨ Exemple de utilizare
<h3>🔔 Automatizare pentru avertizare neplată cu o zi înainte de data scadentă:</h3>

Un exemplu de automatizare pe care o poți crea pentru a nu uita de plata facturii.

```bash
alias: Notificare factura Scomet
description: Notificare cu o zi înainte de data scadență
triggers:
  - trigger: template
    value_template: >
      {% set due_date = states('sensor.scomet_datascadenta') %} {% if
      due_date != 'unknown' and due_date != '' %}
        {{ (as_datetime(due_date) - now()).days == 1 }}
      {% else %}
        false
      {% endif %}
actions:
  - action: notify.mobile_app_sm_g975f
    metadata: {}
    data:
      message: Mâine este ultima zi de plată a facturii tale Scomet
      title: Notificare Factură Scomet
mode: single
```

<h3>🔍 Card pentru afișsarea datelor în Dashboard:</h3>

Un exemplu de cum se pot afișa datele în dashboard.

```bash
type: entities
title: "Scomet: Administrăm confortul"
entities:
  - entity: button.scomet_redirect_button_01jk8kn0vexh8rzgcf30456jbw
  - entity: sensor.scomet_consumaparece
  - entity: sensor.scomet_datafactura
  - entity: sensor.scomet_datascadenta
  - entity: sensor.scomet_nrpersoane
  - entity: sensor.scomet_sold
  - entity: sensor.scomet_total
```

![image](https://github.com/user-attachments/assets/99ff3d63-7101-482a-b2ac-f9492e089297)


# ☕ Susține dezvoltatorul
Dacă îți place această integrare și vrei să sprijini efortul depus, **Buy me a coffee**

<a href="https://www.buymeacoffee.com/geotibi" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

Mulțumesc

## Contribuții

Contribuțiile sunt întotdeauna binevenite! Simte-te liber să vii cu idei noi de îmbunătățire sau să raportezi probleme [aici](https://github.com/geotibi/scomet/issues).

# 🔰Suport
Dacă îți place această integrare, oferă-i o ⭐ pe [GitHub](https://github.com/geotibi/scomet/)! 🙏
