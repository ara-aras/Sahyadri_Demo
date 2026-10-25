# RaktaScan – MVP (Team AAF11, DevHack 2026, PS 3.1)

An anaemia screening aid for ASHA and PHC workers. It works from a photo of the lower eyelid (conjunctiva) taken next to a cheap printed colour card.

**Decision-support aid only. This is NOT a diagnostic device.** Every positive or uncertain result is sent for a blood test.

## What the MVP does
1. **Quality gate**: rejects blurry or badly exposed photos ("Retake photo").
2. **Colour-card calibration**: the white patch on the card corrects for the phone camera and the lighting (daylight vs. warm tube-light).
3. **Pallor index**: redness of the conjunctiva after calibration, compared with group-specific bands (woman / pregnant / child / man).
4. **Abstain and refer**: borderline results are never guessed. The tool says "Not sure – refer for blood test".
5. **Symptom check**: 5 questions can push a borderline "low risk" up to "refer".
6. **Kannada / English** interface with voice output.

## Run it
No install needed. From this folder:
```
python -m http.server 8000
```
Then open http://localhost:8000. It also works on GitHub Pages.

## Honest notes
- `samples/` holds **synthetic test images** made by `make_samples.py`. They are not patient data and only exercise the pipeline.
- The pallor index is a baseline colour rule. In the finale we replace it with a model trained on open datasets: CP-AnemiC (710 conjunctiva images, Ghana, Mendeley), Eyes-defy-anemia (218 images, Italy + India) and open fingernail-Hb sets. We validate across populations (train on Ghana, test on India/Italy).
