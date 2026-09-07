# Aether — first LinkedIn posts (ready to schedule in Postiz)

Post from a **personal profile** (5-10x organic reach vs company page).
Mechanics per `linkedin-playbook.md`:
- No links in the post body — link goes in the first comment; say "link in comments."
- Tue-Thu, 08:00 CET.
- First two lines are all that shows before "…see more."
- Reply to every comment in the first hour.
- Get 5 people to comment (not react) in the first hour.

---

## Post 1 — A1: The convergence problem (no product mention)

> Most operators run two completely separate management worlds and pretend
> they're one network.
>
> The CPE fleet lives in a WiFi cloud — uCentral, TR-369, maybe Plume or Mist.
> Managed by the broadband team.
>
> Transport and RAN live somewhere else entirely — NETCONF and YANG on the
> aggregation gear, SNMP on whatever's too old for that, gNMI if someone
> modernised, A1 policies into a Near-RT RIC if there's a RAN team with budget.
>
> And fixed wireless CPE usually has no dashboard at all.
>
> Two toolchains. Two data models. Two on-call rotations. When a subscriber says
> their connection is bad, nobody can say whether the problem is in the home, the
> backhaul, or the radio — because no single system sees all three.
>
> I keep hearing "converged access" in vendor decks. I have yet to see anyone
> ship a control plane that actually spans it.
>
> Is anyone running fixed and mobile access from one system? Genuinely asking.

**First comment:** (no link — this is a question post, engagement bait)

---

## Post 2 — A2: What we built (the demo video post)

> We manage over 5 million devices. Aether is the platform we built to replace
> the seven stacks underneath that.
>
> Ten protocols in one binary, because the alternative was ten integrations.
>
> CPE side: uCentral, TR-369/USP, WRP for RDK-B, IEEE 1905.1 for EasyMesh,
> OpenSync, MQTT.
>
> Transport and RAN side: NETCONF with YANG models, SNMP for everything too old
> to speak anything better, gNMI for streaming telemetry, and O-RAN A1 plus VES.
>
> One process. One normalized event stream. An OpenWrt router in a living room
> and an A1 policy toward a Near-RT RIC land in the same pipeline.
>
> Rust. The OpenWrt agent is open source; the platform is a managed service
> with EU and US data residency.
>
> We also write the firmware — OpenWRT, OpenWiFi, wlan-ap, RDK-B, QSDK, plus
> camera and IoT — which is why the protocol coverage looks the way it does.
> We've had to live with all of it.
>
> Architecture write-up in the comments.

**First comment:** link to https://aether-io.com + "architecture write-up in the comments"

**Media:** attach `docs/assets/aether-walkthrough.mp4` (53s, 1080×1080, no audio, burned-in captions)

---

## Post 3 — A3: The precision post (the credibility one)

> Let me be exact, because O-RAN rewards precision and punishes marketing.
>
> **Aether is not a RIC.**
>
> What it is: an A1 client and a VES collector. It runs the full A1 policy
> lifecycle against a Near-RT RIC — deliver, withdraw, fetch, enumerate policy
> types, track status — and emits VES events into an ONAP-style OSS. That's the
> integration surface, and it's deliberately narrow.
>
> What that buys you isn't "we do RAN optimization." It's that the same system
> holding your CPE telemetry can act on RAN policy and report into the same OSS
> your RAN already reports into. Correlation happens in one place instead of in a
> spreadsheet.
>
> Want an xApp platform? We are not that. Anyone telling you their WiFi cloud is
> a RIC is selling you something.
>
> The hard part was never A1. It was a data model where a TR-181 parameter from
> an OpenWrt box and a gNMI subscription from an aggregation switch are both
> first-class.
>
> Tell me where this framing is wrong — I'd rather hear it here than in a deployment.

**First comment:** (no link — credibility post, invite pushback)

---

## Post 4 — A4: Fixed wireless, the segment nobody manages

> Every operator I talk to has a growing FWA base and no real way to manage it.
>
> The CPE is an LTE or 5G router. It's in a subscriber's window. Its performance
> depends entirely on radio conditions you can't see from a WiFi dashboard.
>
> So when the customer calls, the answer is a truck roll and someone with a
> signal meter.
>
> ac-client reads the modem through ModemManager and exposes it in the standard
> TR-181 data model — Device.Cellular. IMEI, IMSI, ICCID, and live RSRP, RSRQ and
> SINR, alongside the WiFi telemetry from the same box.
>
> Same agent. Same data model. Same dashboard as the fixed-line fleet.
>
> You can finally answer "is it the radio or the router?" without dispatching anyone.
>
> How are you monitoring FWA CPE today? I suspect the honest answer for most is
> "we aren't."

**First comment:** (no link — question post)

---

## Post 5 — A7: The close

> Aether is running today. Ten protocols, one control plane, from the CPE in the
> home out to O-RAN A1.
>
> Built by a team already managing 5M+ devices, who also write the firmware
> underneath them.
>
> $0.30 per device per month at volume. No per-device AI tax, no separate charge
> for RF optimization or IoT fingerprinting.
>
> The device agent is open source — install it on an OpenWrt box this afternoon
> and see the device appear. The platform is a managed service with EU and US
> data residency; self-hosting is licensed for operators who need it.
>
> Built for a messy access network: multiple CPE silicon vendors, a platform
> inherited from an acquisition, aggregation gear still on SNMP, and fixed
> wireless CPE nobody has a dashboard for.
>
> Pricing and docs in the comments.

**First comment:** link to https://aether-io.com/pricing + docs

---

## Scheduling (Tue-Thu, 08:00 CET)

| Week | Tue | Wed | Thu |
|---|---|---|---|
| Week 1 | Post 1 (A1) | Post 2 (A2 + video) | Post 3 (A3) |
| Week 2 | Post 4 (A4) | Post 5 (A7) | — (reply to comments) |

**Honesty line for the video post:** end with *"Still early. Still ugly in places. But it's real."* — engineers discount polished demos automatically; an admitted rough edge is what makes the rest credible.
