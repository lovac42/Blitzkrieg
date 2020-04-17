# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import re


AUTHOR_HOOK = "L42.BabyOnBoard"

AUTHOR_MESSAGE = """\
The addon(s) listed below were not made for your fancy new version

of Anki. You may continue to use it on this platform unsupported.

But no whining or complaining should any problems occur, mkay?

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""


def getMessageFromAuthor(lang):
    lang2 = lang[:2]

    if lang2 == "ja":
        return """\
下記のアドオンは、Ankiの新しいバージョン用ではありません。

サポートされていないこのプラットフォームで引き続き使用できます。

しかし、何かがうまくいかなくても、怒ったり不満を言ったりしてはいけません。

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""


    if lang2 == "fr":
        return """\
Les add-ons suivants ne sont pas destinés aux nouvelles versions d'Anki. Vous

pouvez continuer à l'utiliser sur cette plate-forme non prise en charge. Mais si

quelque chose ne fonctionne pas, ne vous fâchez pas et ne vous plaignez pas.

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""


    if lang2 == "es":
        return """\
Los siguientes complementos no están pensados para las nuevas

versiones de Anki. Puedes continuar usándolo en esta plataforma

no soportada. Pero si algo no funciona, no te enfades o te quejes.

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""


    if lang2 == "gl":
        return """\
Die folgenden Add-ons sind nicht für neue Versionen von Anki vorgesehen.

Sie können sie weiterhin auf dieser nicht unterstützten Plattform verwenden.

Aber wenn etwas nicht funktioniert, ärgern oder beschweren Sie sich nicht.

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""



    if lang2 == "it":
        return """\
I seguenti componenti aggiuntivi non sono destinati alle nuove versioni di

Anki. È possibile continuare a utilizzarlo su questa piattaforma non supportata.

Ma se qualcosa non funziona, non arrabbiatevi e non lamentatevi.

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""




    if lang2 == "ru":
        return """\
Следующие дополнения не предназначены для новых версий Anki.

Вы можете продолжать использовать его на этой неподдерживаемой

платформе. Но если что-то не работает, не сердитесь и не жалуйтесь.

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""



    lang = re.sub(r"[_-]", '', lang)


    if lang == "zhTW":
        return """\
以下附加組件不適用於較新版本的Anki。

您可以在不受支持的平台上繼續使用它。

但是，如果出現問題，你不要生氣也不要抱怨。

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""


    if lang == "zhCN":
        return """\
以下附加组件不适用于较新版本的Anki。

您可以在不受支持的平台上继续使用它。

但是，如果出现问题，你不要生气也不要抱怨。

    —L42   (╯°□°)╯︵ ┻━┻
_________________________________________________________
%s"""

    return AUTHOR_MESSAGE
