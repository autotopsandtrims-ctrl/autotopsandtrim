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
    3.33.130.190     <- GoDaddy domain forwarding, must go
    15.197.148.33    <- GoDaddy domain forwarding, must go
    216.198.79.1     <- Vercel, this is the only correct one
  Traffic round-robins between all three, so it intermittently hits GoDaddy's
  forwarding service instead of Vercel, and that service has no certificate for
  this domain.
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

7. FIRST, turn off domain forwarding. This is the step people miss.
   Look for "Forwarding" (it may be a separate tab, or a section under the DNS
   records list). If there is a forwarding rule on the domain or the root/@ host,
   DELETE / DISABLE it.
   Why this matters: 3.33.130.190 and 15.197.148.33 ARE GoDaddy's forwarding
   service. If you delete those A records while forwarding is still switched on,
   GoDaddy will silently put them back and the problem will return.

8. Now in the DNS records list, find every A record whose Name/Host is "@".
   - DELETE the A record pointing to 3.33.130.190
   - DELETE the A record pointing to 15.197.148.33
   - KEEP exactly ONE A record for "@", pointing at the IP Vercel showed you in
     step 5. If the existing one already matches, leave it. If it does not, edit
     it to match.
   End state: exactly one "@" A record, and nothing else pointing the apex
   anywhere else.

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
