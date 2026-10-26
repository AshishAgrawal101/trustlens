"""One CPU QR decode, isolated from the server and killed on timeout."""
import json
import os
from pathlib import Path
import sys


def main():
    # Use the running app's installed environment without the Windows venv redirector.
    prefix = Path(sys.argv[2])
    packages = prefix/('Lib/site-packages' if os.name=='nt' else f'lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages')
    sys.path.insert(0, str(packages))
    def audit(event, args):
        if (event.startswith('socket.') and event!='socket.gethostname') or event in ('subprocess.Popen','os.system','os.startfile','os.posix_spawn'):
            raise RuntimeError('QR decoding cannot access the network or start another program')
    sys.addaudithook(audit)
    import cv2
    cv2.setNumThreads(1)
    cv2.ocl.setUseOpenCL(False)
    image = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
    if image is None or image.size>3000*3000:
        raise ValueError('QR input could not be read within its size limit')
    detector = cv2.QRCodeDetector()
    found, values, _, _ = detector.detectAndDecodeMulti(image)
    codes = [value for value in values if value] if found else []
    if not codes:
        value, _, _ = detector.detectAndDecode(image)
        if value: codes.append(value)
    too_large = len(codes)>16 or len('\n'.join(codes))>30000
    sys.stdout.write(json.dumps({'codes': [] if too_large else codes, 'too_large': too_large}, ensure_ascii=True))


if __name__=='__main__':
    main()
