# Historical quotation context increment

The shared English request matcher now marks request wording inside a small set of explicitly completed teaching quotations as unknown context with zero weight. Current or ambiguous quotations retain warnings; an independent request after the quotation still triggers its own evidence. This does not authenticate intent or establish safety. Unsupported frames retain existing behavior.

Root verification: 248 app tests passed with zero skips, including native Windows OCR and actual C2PA signing/tampering. Three live API checks confirmed historical versus current quotations and a later live request. The eight protected image/C2PA runtime files remain byte-identical. The unchanged frontend retains its previous 17 offline controller passes; no new browser visual/keyboard verification occurred.

These are constructed development regressions, not population accuracy. Earlier 24-case initial results remain preserved and are not silently replaced. A broad root pytest invocation also collected experimental artifact tests whose no-heavy-import assumptions conflict with app imports; three such isolation tests failed. The corrected explicit tests/ invocation passed. Experimental tests run separately in their intended stdlib processes.

The optional local NLI model remains experimental and is not installed in the app. Its first import took 62.47 seconds, exceeding the planned 60-second full cold-load target. Image comparison still has no real features fitted or scored.

Follow-up: adding only the explicit subject “an unexpected caller” to the existing stop/hang-up advice recognizer passed 255 app tests (zero skips, including native OCR/C2PA). On the same examined 24 cases, 22 contracts now pass with zero unwanted present-request warnings and two retained reference omissions; none of the previously passing 21 regressed. This remains examined regression evidence.
