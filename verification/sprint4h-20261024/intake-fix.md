# Bounded intake transport and derived-image cleanup

Root authorized only app/analyzers/qr.py, screenshot.py, the new dedicated regression and ownedintakeverification. Checked currentprotected34list in result-first preservation receipt beforeediting: neitherhelper isprotected. No decoder/model/trust/weights/metadata or otherappfile changed.

Eightnewtests ran beforeedits:6failed,2passed. High/low loneJSONsurrogates caused actualQR/OCRroute500s; derivedgrayscale images stayedopen aftersuccess/savefailure. ValidJSONsurrogatepairs representingastralcharacters already passed andremain unchanged.

Fix: afterexistingtype/length/controlvalidation, strictlyUTF8encode theboundedworkertext as validation only. Lone surrogate failures followexistingValueError->fixedunavailable503 handling; textisnot rewritten/replaced/normalized. QR retains all existingCc/bidicontrol policy and OCR retains exacten-USvalidation. Café/Japanese/emoji/musicclefvalidUnicode output roundtrips exactly with review_required=true. No request/sourcepath/filename/workercontent appears inerrors.

QR's grayscaleconversion now has itsowncontextlib.closing aroundPNGsave. BothsourceRGB andderivedLpixelsclose explicitly; tempdirectory/lock/worker preprocessing/limits unchanged. Newtests retainimage/errorreferences toproveclose on success and simulatedOSError without invokingnativeworkers. Noimagerecognition/accuracyclaim isadded.

Combined meaningful transport/QR/OCRlifecycle/fileintake/malformedPNG/uploadlimit suite:93passed,zero skips in5.49seconds. Existingfileintake includesnativegeneratedQRfixtures; noOCRnativejob,imageoriginmodel,privateasset,networkdestination,download orbrowserupload was used. The new8tests themselves use2x2constructedPNG/fakeworker only. No model/candidate/release null was replaced; STOP/resource/license/final-datarestrictions remainunchanged.
