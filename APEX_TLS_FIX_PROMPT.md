# Browser-agent prompt — fix the apex domain TLS certificate

Copy everything inside the fence below and give it to the browser agent.
The user must already be signed in to both Vercel and GoDaddy.

---

```
GOAL
Make https://autotopsandtrim.com (no "www") load without a certificate warning,
by redirecting it to https://www.autotopsandtrim.com.

Right now the apex domain has no valid TLS certificate. The certificate that is
served covers only "www.autotopsandtrim.com", so any visitor who types the
domain without "www" gets a browser security warning.

VERIFIED CURRENT STATE (checked 2026-08-05, do not assume it has changed)
- autotopsandtrim.com resolves to THREE A records:
    3.33.130.190     <- GoDaddy parking server, must go
    15.197.148.33    <- GoDaddy parking server, must go
    216.198.79.1     <- Vercel, this is the only correct one
  Traffic round-robins between all three, so it intermittently hits GoDaddy's
  parking service instead of Vercel, and that service has no certificate for
  this domain.
- In the GoDaddy panel this appears as a SINGLE record: an A record on "@" whose
  Data column reads "Parked". Deleting that one row removes both bad IPs.
- www.autotopsandtrim.com is a CNAME to eab5c7f6899029eb.vercel-dns-017.com and
  works correctly. DO NOT TOUCH IT.
- DNS is hosted at GoDaddy (nameservers ns49.domaincontrol.com and
  ns50.domaincontrol.com).
- The Vercel project is "hopeton-website" under the team/scope
  "auto-top-and-trim".

There are TWO halves. Both are required. Doing only one will not fix it.

=== PART A — Vercel ===
1. Go to https://vercel.com and open the project "hopeton-website" in the
   "auto-top-and-trim" scope.
2. Settings -> Domains.
3. Check whether "autotopsandtrim.com" (the bare apex, no www) is listed.
   - The user removed it previously, so it is probably NOT there.
   - If it is missing, click "Add Domain" and add exactly: autotopsandtrim.com
4. When Vercel asks how to configure it, choose the option that REDIRECTS the
   apex to www.autotopsandtrim.com. Wording varies; pick the choice that makes
   autotopsandtrim.com redirect to www.autotopsandtrim.com, NOT the reverse, and
   not "no redirect".
5. Vercel will then display the DNS record it wants for the apex — an A record
   with a specific IP address.
   *** READ THAT IP OFF THE SCREEN AND WRITE IT DOWN. ***
   Do NOT assume it is 216.198.79.1. Vercel has changed this address before.
   Report the exact value you see.

=== PART B — GoDaddy DNS ===
6. Go to https://dcc.godaddy.com/control/portfolio and open DNS for
   autotopsandtrim.com.

7. The DNS panel has been inspected already (2026-08-05). There are exactly TWO
   A records on "@":

     A   @   216.198.79.1    600 seconds     <- Vercel. KEEP THIS.
     A   @   Parked          600 seconds     <- DELETE THIS ONE.

   The second row literally shows the word "Parked" in the Data column instead of
   an IP address. That is GoDaddy's domain-parking record, and it is the entire
   cause of the problem: it expands to GoDaddy's parking servers 3.33.130.190 and
   15.197.148.33, which is why an external DNS lookup returns three addresses
   while the panel only lists two. Its propagation icon is greyed out, unlike the
   real record's.

   DELETE the "Parked" A record. That is the whole fix on the DNS side.

   If the panel instead shows literal A records for 3.33.130.190 or
   15.197.148.33, delete those, and also check for a "Forwarding" section and
   disable any rule there — otherwise GoDaddy will re-create them.

   End state: exactly ONE "@" A record, matching the IP Vercel showed in step 5.

8. Do NOT delete these, which are all present and correct:
     CNAME  www             -> eab5c7f6899029eb.vercel-dns-017.com
     MX     @               -> smtp.google.com (priority 1)  ** the shop's email **
     NS     @               -> ns49 / ns50.domaincontrol.com
     CNAME  _domainconnect  -> _domainconnect.gd.domaincontrol.com
     SOA    @

   Note: there are also two TXT records on "@" containing IP addresses
   (15.197.148.33 and 216.198.79.1). Those are somebody's mistake — IPs pasted
   into the wrong record type — and they have no effect on routing. LEAVE THEM
   ALONE; removing them is not part of this task.

9. DO NOT MODIFY ANY OF THE FOLLOWING. Changing these will break the website or
   the shop's email:
   - the "www" CNAME record
   - any MX records (email)
   - any TXT records (SPF, DKIM, domain verification)
   - the nameservers

=== VERIFY ===
10. Wait about 10 minutes for DNS to propagate, then confirm ALL of these:
    a. https://autotopsandtrim.com loads with NO certificate warning and lands
       on https://www.autotopsandtrim.com
    b. https://www.autotopsandtrim.com still loads normally
    c. A DNS lookup of autotopsandtrim.com returns exactly ONE A record, and it
       matches the IP from step 5
    If the certificate is still warning after 10 minutes, go back to Vercel ->
    Settings -> Domains and check whether the apex shows a pending or invalid
    configuration. Vercel issues the certificate only once DNS is correct, and
    that can take up to an hour.

=== REPORT BACK ===
Tell me:
- Whether autotopsandtrim.com was already in Vercel or had to be added
- The exact IP address Vercel asked for in step 5
- Whether GoDaddy domain forwarding was switched on, and whether you removed it
- Which A records you deleted
- The result of each of the three checks in step 10
- Anything that did not match these instructions

If anything looks different from what is described here, STOP and describe what
you see rather than guessing. Do not change nameservers, do not transfer the
domain, and do not modify MX or TXT records under any circumstances.
```
