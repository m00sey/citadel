import io
import base64
from time import sleep
from urllib.parse import urlparse, urljoin

import flet as ft
import qrcode
from citadel.tasks import aiding
from flet_core import padding
from keri import kering
from keri.app import habbing, directing
from keri.app.keeping import Algos
from keri.core import coring
from keri.db import dbing


class Identifiers(ft.Column):

    def __init__(self, app):
        self.app = app

        self.title = ft.Text("Identifiers", size=32)
        self.list = ft.Column([], spacing=0, expand=True)
        self.card = ft.Container(
            content=self.list,
            padding=padding.only(left=10, top=15), expand=True,
            alignment=ft.alignment.top_left
        )

        super(Identifiers, self).__init__([
            ft.Row([ft.Icon(ft.icons.PEOPLE_ALT_SHARP, size=32), self.title]),
            ft.Row([self.card])
        ], expand=True, scroll=ft.ScrollMode.ALWAYS)

    def add_identifier(self, _):
        self.title.value = "Create Identifier"
        self.app.page.floating_action_button = None

        identifierPanel = CreateIdentifierPanel(self.app)
        self.card.content = identifierPanel
        self.card.update()
        self.app.page.update()

        identifierPanel.update()

    def setIdentifiers(self, habs):
        self.title.value = "Identifiers"
        self.card.content = self.list
        self.list.controls.clear()
        icon = ft.icons.PERSON_SHARP
        tip = "Identifier"
        for hab in habs:
            if isinstance(hab, habbing.GroupHab):
                icon = ft.icons.PEOPLE_ALT_OUTLINED
                tip = "Group Multisig"
            if hab.algo == Algos.salty:
                icon = ft.icons.LINK_OUTLINED
                tip = "Key Chain"
            elif hab.algo == Algos.randy:
                icon = ft.icons.SHUFFLE_OUTLINED
                tip = "Random Key"

            tile = ft.ListTile(
                leading=ft.Icon(icon, tooltip=tip),
                title=ft.Text(hab.name),
                subtitle=ft.Text(hab.pre, font_family="SourceCodePro"),
                trailing=ft.PopupMenuButton(
                    tooltip=None,
                    icon=ft.icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(text="View", icon=ft.icons.PAGEVIEW, on_click=self.viewIdentifier,
                                         data=hab),
                        ft.PopupMenuItem(text="Delete", icon=ft.icons.DELETE_FOREVER),
                    ],
                ),
                on_click=self.viewIdentifier,
                data=hab,
            )
            self.list.controls.append(tile)

        self.update()

    def viewIdentifier(self, e):
        hab = e.control.data

        viewPanel = ViewIdentifierPanel(self.app, hab)
        self.card.content = viewPanel
        self.card.update()
        self.app.page.update()

        viewPanel.update()

    def build(self):
        return ft.Column([
            ft.Row([ft.Icon(ft.icons.PEOPLE_ALT_SHARP, size=32), self.title]),
            ft.Row([self.card])
        ], expand=True)


class ViewIdentifierPanel(ft.UserControl):

    def __init__(self, app, hab):
        self.app = app
        self.hab = hab

        if isinstance(hab, habbing.GroupHab):
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Group Multisig Identifier", weight=ft.FontWeight.BOLD),
            ])
        elif hab.algo == Algos.salty:
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Hierarchical Key Chain Identifier", weight=ft.FontWeight.BOLD),
            ])
        elif hab.algo == Algos.randy:
            self.typePanel = ft.Row([
                ft.Text("Key Type:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text("Random Key Generation Identifier", weight=ft.FontWeight.BOLD),
            ])

        self.publicKeys = ft.Column()
        for idx, verfer in enumerate(self.hab.kever.verfers):
            self.publicKeys.controls.append(ft.Row([
                ft.Text(str(idx + 1)),
                ft.Text(verfer.qb64, font_family="SourceCodePro")
            ]))

        self.oobiTabs = ft.Column()

        def copy(e):
            self.app.page.set_clipboard(e.control.data)

            self.page.snack_bar = ft.SnackBar(ft.Text(f"OOBI URL Copied!"), duration=2000)
            self.page.snack_bar.open = True
            self.page.update()

        for role in ('agent', 'mailbox', 'witness'):
            oobi = self.loadOOBIs(role)

            if len(oobi) == 0:
                continue

            img = qrcode.make(oobi[0])
            f = io.BytesIO()
            img.save(f)
            f.seek(0)

            self.oobiTabs.controls.append(ft.Column([
                ft.Row([
                    ft.Text(role.capitalize(), weight=ft.FontWeight.BOLD),
                ]),
                ft.Row([
                    ft.Image(src_base64=base64.b64encode(f.read()).decode('utf-8'), width=175)
                ]),
                ft.Row([
                    ft.Text(value=oobi[0], tooltip=oobi[0], max_lines=3, size=12, overflow=ft.TextOverflow.ELLIPSIS,
                            weight=ft.FontWeight.BOLD, font_family="SourceCodePro", width=300),

                    ft.IconButton(icon_color=ft.colors.BLUE_400, icon=ft.icons.COPY_SHARP, data=oobi[0],
                                  on_click=copy)
                ]),
                ft.Container(padding=ft.padding.only(top=6)),

            ]))

        super(ViewIdentifierPanel, self).__init__()

    def build(self):
        kever = self.hab.kever
        ser = kever.serder
        dgkey = dbing.dgKey(ser.preb, ser.saidb)
        wigs = self.hab.db.getWigs(dgkey)
        return ft.Container(ft.Column([
            ft.Container(content=ft.Divider(color="#51dac5"), padding=ft.padding.only(bottom=10)),
            ft.Row([
                ft.Text("Alias:", weight=ft.FontWeight.BOLD, width=175, size=14),
                ft.Text(self.hab.name, size=14, weight=ft.FontWeight.BOLD)
            ]),
            ft.Row([
                ft.Text("Prefix:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text(self.hab.pre, font_family="SourceCodePro")
            ]),
            ft.Row([
                ft.Text("Establishment Only", weight=ft.FontWeight.BOLD, width=168, size=14),
                ft.Checkbox(value=True, fill_color="#51dac5", disabled=True)
            ], visible=kever.estOnly),
            ft.Row([
                ft.Text("Sequence Number:", weight=ft.FontWeight.BOLD, width=175),
                ft.Text(kever.sner.num)
            ]),
            self.typePanel,
            ft.Container(content=ft.Divider(color="#51dac5"), padding=ft.padding.only(top=10, bottom=10)),
            ft.Column([
                ft.Row([
                    ft.Text("Witnesses:", weight=ft.FontWeight.BOLD, width=175),
                ]),
                ft.Row([
                    ft.Text("Count:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(str(len(self.hab.kever.wits)))
                ]),
                ft.Row([
                    ft.Text("Receipt:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(str(len(wigs)))
                ]),
                ft.Row([
                    ft.Text("Threshold:", weight=ft.FontWeight.BOLD, width=175),
                    ft.Text(kever.toader.num)
                ]),
            ]),
            ft.Container(content=ft.Divider(color="#51dac5"), padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.Text("Public Keys:", weight=ft.FontWeight.BOLD, width=175),
            ]),
            ft.Container(content=self.publicKeys, padding=ft.padding.only(left=40)),
            ft.Container(content=ft.Divider(color="#51dac5"), padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.Text("OOBIs:", weight=ft.FontWeight.BOLD, width=175),
            ]),
            ft.Container(content=self.oobiTabs),
            ft.Container(content=ft.Divider(color="#51dac5"), padding=ft.padding.only(top=10, bottom=10)),
            ft.Row([
                ft.TextButton("Close", on_click=self.close)
            ]),
        ]), expand=True, alignment=ft.alignment.top_left,
            padding=padding.only(left=10, top=15))

    def loadOOBIs(self, role):
        if role in (kering.Roles.witness,):  # Fetch URL OOBIs for all witnesses
            oobis = []
            for wit in self.hab.kever.wits:
                urls = self.hab.fetchUrls(eid=wit, scheme=kering.Schemes.http) or self.hab.fetchUrls(eid=wit, scheme=kering.Schemes.https)
                if not urls:
                    return []

                url = urls[kering.Schemes.http] if kering.Schemes.http in urls else urls[kering.Schemes.https]
                up = urlparse(url)
                oobis.append(urljoin(up.geturl(), f"/oobi/{self.hab.pre}/witness/{wit}"))
            return oobis

        elif role in (kering.Roles.controller,):  # Fetch any controller URL OOBIs
            oobis = []
            urls = self.hab.fetchUrls(eid=self.hab.pre, scheme=kering.Schemes.http) or self.hab.fetchUrls(eid=self.hab.pre, scheme=kering.Schemes.https)
            if not urls:
                return []

            url = urls[kering.Schemes.http] if kering.Schemes.http in urls else urls[kering.Schemes.https]
            up = urlparse(url)
            oobis.append(urljoin(up.geturl(), f"/oobi/{self.hab.pre}/controller"))
            return oobis

        elif role in (kering.Roles.agent,):
            oobis = []
            roleUrls = (self.hab.fetchRoleUrls(self.hab.pre, scheme=kering.Schemes.http, role=kering.Roles.agent)
                        or self.hab.fetchRoleUrls(self.hab.pre, scheme=kering.Schemes.https, role=kering.Roles.agent))
            if not roleUrls:
                return []

            for eid, urls in roleUrls['agent'].items():
                url = urls[kering.Schemes.http] if kering.Schemes.http in urls else urls[kering.Schemes.https]
                up = urlparse(url)
                oobis.append(urljoin(up.geturl(), f"/oobi/{self.hab.pre}/agent/{eid}"))

            return oobis

        return []

    def close(self, _):
        self.app.showIdentifiers()


class CreateIdentifierPanel(ft.UserControl):
    def __init__(self, app):
        self.app = app
        super(CreateIdentifierPanel, self).__init__()

        self.alias = ft.TextField(label="Alias", border_color="#51dac5")
        self.eo = ft.Checkbox(label="Establishment only", value=False, fill_color="#51dac5")

        salt = coring.randomNonce()[2:23]
        self.salt = ft.TextField(label="Key Salt", value=salt, password=True, can_reveal_password=True, width=300,
                                 border_color="#51dac5")
        self.keyCount = ft.TextField(label="Signing", width=100, value="1", border_color="#51dac5")
        self.nkeyCount = ft.TextField(label="Rotation", width=100, value="1", border_color="#51dac5")
        self.keySith = ft.TextField(label="Signing Threshold", width=200, value="1", border_color="#51dac5")
        self.nkeySith = ft.TextField(label="Rotation Threshold", width=200, value="1", border_color="#51dac5")
        self.toad = ft.TextField(label="Witness Threshold", width=150, value="0", border_color="#51dac5")

        self.signingList = ft.Column(width=550)
        self.signingDropdown = ft.Dropdown(options=[], width=420, text_size=12, height=50,
                                           border_color="#51dac5",
                                           text_style=ft.TextStyle(font_family="SourceCodePro"))
        self.rotationList = ft.Column(width=550)
        self.rotationDropdown = ft.Dropdown(options=[], width=420, text_size=12, height=50,
                                            border_color=ft.colors.with_opacity(0.25, ft.colors.GREY), disabled=True,
                                            text_style=ft.TextStyle(font_family="SourceCodePro"))
        self.rotationAddButton = ft.IconButton(icon=ft.icons.ADD, tooltip="Add Member", on_click=self.addRotation,
                                               disabled=True)
        self.rotSith = ft.TextField(label="Rotation Threshold", width=200, value="1", border_color="#51dac5",
                                    disabled=True)

        def resalt(_):
            self.salt.value = coring.randomNonce()[2:23]
            self.salt.update()

        self.salty = ft.Column([
            ft.Row([
                self.salt,
                ft.IconButton(icon=ft.icons.CHANGE_CIRCLE_OUTLINED, on_click=resalt, icon_color="#51dac5")
            ]),
            ft.Text("Number of Keys / Threshold"),
            ft.Row([
                self.keyCount,
                self.keySith
            ]),
            ft.Row([
                self.nkeyCount,
                self.nkeySith
            ])

        ], spacing=20)

        self.randy = ft.Column([
            ft.Text("Number of Keys / Threshold"),
            ft.Row([
                self.keyCount,
                self.keySith
            ]),
            ft.Row([
                self.nkeyCount,
                self.nkeySith
            ])
        ], spacing=20)

        self.group = ft.Column([
            ft.Text("Signing members"),
            self.signingList,
            ft.Row([
                self.signingDropdown,
                ft.IconButton(icon=ft.icons.ADD, tooltip="Add Member", on_click=self.addMember)
            ]),
            ft.Row([
                self.keySith
            ]),
            ft.Container(padding=ft.padding.only(top=20)),
            ft.Checkbox(label="Rotation Members (if different from signing)", value=False,
                        on_change=self.enableRotationMembers),
            self.rotationList,
            ft.Row([
                self.rotationDropdown,
                self.rotationAddButton
            ]),
            ft.Row([
                self.rotSith
            ])

        ], spacing=15)

        self.witnesses = self.loadWitnesses()

        self.keyTypePanel = ft.Container(content=self.salty, padding=padding.only(left=50))
        self.keyType = "salty"

        self.witnessDropdown = ft.Dropdown(options=self.witnesses, width=420, text_size=14,
                                           border_color="#51dac5",
                                           text_style=ft.TextStyle(font_family="SourceCodePro"))
        self.witnessList = ft.Column(width=550)

        self.members = self.loadMembers()
        self.signingDropdown.options = self.members
        self.rotationDropdown.options = list(self.members)

    def keyTypeChanged(self, e):
        self.keyType = e.control.value
        match e.control.value:
            case "salty":
                self.keyTypePanel.content = self.salty
            case "randy":
                self.keyTypePanel.content = self.randy
            case "group":
                self.keyTypePanel.content = self.group
        self.update()

    def addWitness(self, _):
        if not self.witnessDropdown.value:
            return

        self.witnessList.controls.append(
            ft.ListTile(title=ft.Text(self.witnessDropdown.value, font_family="SourceCodePro"),
                        trailing=ft.IconButton(ft.icons.DELETE_OUTLINED, icon_color=ft.colors.RED_400,
                                               on_click=self.deleteWitness, data=self.witnessDropdown.value),
                        data=self.witnessDropdown.value),
        )

        for option in self.witnessDropdown.options:
            if option.key == self.witnessDropdown.value:
                self.witnessDropdown.options.remove(option)

        self.toad.value = str(self.recommendedThold(len(self.witnessList.controls)))
        self.toad.update()
        self.witnessDropdown.value = None
        self.witnessDropdown.update()
        self.witnessList.update()

    def deleteWitness(self, e):
        aid = e.control.data
        for tile in self.witnessList.controls:
            if tile.data == aid:
                self.witnessList.controls.remove(tile)
                self.witnessDropdown.options.append(ft.dropdown.Option(aid))
                break

        self.toad.value = str(self.recommendedThold(len(self.witnessList.controls)))
        self.toad.update()
        self.witnessDropdown.update()
        self.witnessList.update()

    def addMember(self, _):
        if self.signingDropdown.value is None:
            return

        idx = int(self.signingDropdown.value)
        m = self.app.members[idx]
        self.signingList.controls.append(
            ft.ListTile(title=ft.Text(f"{m['alias']}\n({m['id']})", font_family="SourceCodePro", size=14),
                        trailing=ft.IconButton(ft.icons.DELETE_OUTLINED, icon_color=ft.colors.RED_400,
                                               on_click=self.deleteMember, data=self.signingDropdown.value),
                        data=self.signingDropdown.value),
        )

        for option in self.signingDropdown.options:
            if option.key == self.signingDropdown.value:
                self.signingDropdown.options.remove(option)

        self.signingDropdown.value = None
        self.signingDropdown.update()
        self.signingList.update()

    def enableRotationMembers(self, e):
        self.rotationDropdown.disabled = not e.control.value
        self.rotSith.disabled = not e.control.value
        self.rotationAddButton.disabled = not e.control.value
        self.rotationList.controls.clear()

        self.rotationDropdown.border_color = "#51dac5" if e.control.value \
            else ft.colors.with_opacity(0.25, ft.colors.GREY)

        self.rotationList.update()
        self.rotationDropdown.update()
        self.rotSith.update()
        self.rotationAddButton.update()

    def addRotation(self, _):
        if self.rotationDropdown.value is None:
            return

        idx = int(self.rotationDropdown.value)
        m = self.app.members[idx]
        self.rotationList.controls.append(
            ft.ListTile(title=ft.Text(self.rotationDropdown.value, font_family="SourceCodePro", size=14),
                        trailing=ft.IconButton(ft.icons.DELETE_OUTLINED, icon_color=ft.colors.RED_400,
                                               on_click=self.deleteRotation, data=self.rotationDropdown.value),
                        data=self.rotationDropdown.value),
        )

        for option in self.rotationDropdown.options:
            if option.key == self.rotationDropdown.value:
                self.rotationDropdown.options.remove(option)

        self.rotationDropdown.value = None
        self.rotationDropdown.update()
        self.rotationList.update()

    def deleteMember(self, e):
        aid = e.control.data
        for tile in self.signingList.controls:
            if tile.data == aid:
                self.signingList.controls.remove(tile)
                self.signingDropdown.options.append(ft.dropdown.Option(aid))
                break

        self.toad.value = str(self.recommendedThold(len(self.signingList.controls)))
        self.toad.update()
        self.signingDropdown.update()
        self.signingList.update()

    def deleteRotation(self, e):
        aid = e.control.data
        for tile in self.rotationList.controls:
            if tile.data == aid:
                self.rotationList.controls.remove(tile)
                self.rotationDropdown.options.append(ft.dropdown.Option(aid))
                break

        self.toad.value = str(self.recommendedThold(len(self.rotationList.controls)))
        self.toad.update()
        self.rotationDropdown.update()
        self.rotationList.update()

    def createAid(self, _):

        if self.alias.value == "":
            return

        if self.salt.value == "" or len(self.salt.value) != 21:
            return

        kwargs = dict(algo=self.keyType)
        if self.keyType == "salty":
            kwargs['salt'] = coring.Salter(raw=self.salt.value.encode("utf-8")).qb64
            kwargs['icount'] = int(self.keyCount.value)
            kwargs['isith'] = int(self.keySith.value)
            kwargs['ncount'] = int(self.nkeyCount.value)
            kwargs['nsith'] = int(self.nkeySith.value)

        elif self.keyType == "randy":
            kwargs['salt'] = None
            kwargs['icount'] = int(self.keyCount.value)
            kwargs['isith'] = int(self.keySith.value)
            kwargs['ncount'] = int(self.nkeyCount.value)
            kwargs['nsith'] = int(self.nkeySith.value)

        elif self.keyType == "group":
            kwargs['isith'] = int(self.keySith.value)
            kwargs['nsith'] = int(self.nkeySith.value)

            states = []
            for tile in self.signingList.controls:
                m = self.app.members[int(tile.data)]
                states = self.app.hby.keyStates()
                state = states.get(m['id'])
                states.append(state[0])

            if not self.rotSith.disabled:
                rstates = []
                for tile in self.rotationList.controls:
                    m = self.app.members[int(tile.data)]
                    states = self.app.hby.keyStates()
                    state = states.get(m['id'])
                    rstates.append(state[0])
            else:
                rstates = states

            kwargs["states"] = states
            kwargs["rstates"] = rstates

        kwargs['wits'] = [c.data for c in self.witnessList.controls]
        kwargs['toad'] = self.toad.value
        kwargs['estOnly'] = self.eo.value

        self.page.snack_bar = ft.SnackBar(ft.Text(f"Creating {self.alias.value}..."), duration=5000)
        self.page.snack_bar.open = True
        self.page.update()

        if self.keyType == "group":
            hab = self.app.hby.makeGroupHab(name=self.alias.value, **kwargs)
        else:
            hab = self.app.hby.makeHab(name=self.alias.value, **kwargs)
            directing.runController([aiding.Incepter(hby=self.app.hby, hab=hab)])

        self.page.snack_bar = ft.SnackBar(ft.Text(f"Identifier {hab.pre} created!"), duration=2000)
        self.page.snack_bar.open = True
        self.page.update()

        self.reset()
        self.app.showIdentifiers()

    def loadWitnesses(self):
        return [ft.dropdown.Option(wit['id']) for wit in self.app.witnesses]

    def loadMembers(self):
        return [ft.dropdown.Option(key=idx, text=f"{m['alias']}\n({m['id']})") for idx, m in enumerate(self.app.members)]

    def cancel(self, _):
        self.reset()
        self.app.showIdentifiers()

    def reset(self):
        self.alias.value = ""
        self.keyTypePanel = ft.Container(content=self.salty, padding=padding.only(left=50))
        self.keyType = "salty"
        self.nkeySith.value = "1"
        self.keySith.value = "1"
        self.nkeyCount.value = "1"
        self.keyCount.value = "1"
        self.salt.value = coring.randomNonce()[2:23]

    @staticmethod
    def recommendedThold(numWits):
        match numWits:
            case 0:
                return 0
            case 1:
                return 1
            case 2 | 3:
                return 2
            case 4:
                return 3
            case 5 | 6:
                return 4
            case 7:
                return 5
            case 8 | 9:
                return 7
            case 10:
                return 8

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.alias,
                    self.eo
                ]),
                ft.Column([
                    ft.Text("Select Key Type"),
                    ft.RadioGroup(content=ft.Row([
                        ft.Radio(value="salty", label="Key Chain"),
                        ft.Radio(value="randy", label="Random Key"),
                        ft.Radio(value="group", label="Group Multisig")]), value="salty", on_change=self.keyTypeChanged)
                ]),
                self.keyTypePanel,
                ft.Container(content=ft.Divider(color="#51dac5"), padding=ft.padding.only(top=10, bottom=2)),
                ft.Column([
                    ft.Text("Witnesses"),
                    self.witnessList,
                    ft.Row([
                        self.witnessDropdown,
                        ft.IconButton(icon=ft.icons.ADD, tooltip="Add Witness", on_click=self.addWitness)
                    ]),
                    ft.Container(padding=ft.padding.only(top=3)),
                    ft.Row([
                        ft.Text("Threshold of Acceptable Duplicity"),
                        self.toad
                    ])
                ]),
                ft.Container(content=ft.Divider(color="#51dac5"), padding=ft.padding.only(top=10, bottom=10)),
                ft.Row([
                    ft.TextButton("Create", on_click=self.createAid),
                    ft.TextButton("Cancel", on_click=self.cancel)
                ])
            ], spacing=35, scroll=ft.ScrollMode.AUTO),
            expand=True, alignment=ft.alignment.top_left,
            padding=padding.only(left=10, top=15))
