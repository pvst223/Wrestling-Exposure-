# Exact remaining dependency specification (UNRESOLVED; nothing below has been obtained or substituted)
The full experiment requires THREE frozen feature backbones. One is pinned; two are not.
## A. Pinned and hashed
MobileCLIP-B image encoder (TorchScript mobileclip_blt.ts) sha256 a67804d1b0f07b8b9a20c1761ec0847f34660f5fa338ec70e8f3fce68ed95e54; loaded by the V0.5 loader (adapter `mobileclip_b`). General image embedding, not person re-ID. Person detector (not a backbone for identity): YOLOv8m-pose v8.3.0 sha dbe539ea268db2534390942cfdf206e521f376f19e5415967a57f6a2ddfa3c90.
## B. To be pinned by Chat/investigator BEFORE any result is generated
For EACH of (1) a pretrained person re-ID backbone and (2) DINOv2-small, the following record must be supplied and written to the registry (Claude fills the hashes it can compute):
1. Exact model name and variant (e.g. architecture identifier) and the training data it was pretrained on (the re-ID model's training datasets must be stated, because overlap with wrestling/broadcast footage or the test identities is a leakage question).
2. Exact weight file name and sha256 (supplied as a file attachment; Claude computes and records the hash; a mismatch with a stated hash halts the run).
3. Source URL, repository commit or release tag, and licence.
4. Loader: either a timm architecture name loadable by adapter `timm_local` with ALL keys matching (the adapter now refuses a partial load: any missing key aborts), or the exact loader code (file + sha256). If the re-ID model needs another framework (e.g. torchreid/ CLIP-ReID code), the investigator supplies that code or approves an adapter `reid_local` which Claude writes and which is reviewed and hashed before use.
5. Input spec: input size, mean/std, channel order, crop/letterbox convention (default: the frozen 224 letterbox with pad 114 unless the model requires another size; any size change is part of the pinned record and applied before results).
6. Output spec: embedding layer and dimension, normalisation (L2) applied by the heads, and a deterministic reference check: a fixed synthetic input (seeded) must give an embedding whose sha256 is recorded at pinning time and re-verified before extraction.
7. Python/package versions needed (torch, timm or other), recorded in the run manifest.
## C. Pre-run acceptance checks (automatic, in pipeline_guard / registry)
Weights hash matches the pinned record; strict state-dict load; reference embedding hash matches; feature cache key = sha256(video, detections, crop params, backbone id, weights hash); registry ledger entry created before extraction; no result file exists before the preregistration is approved and hashed.
## D. Policy
No generic ImageNet/other backbone may stand in for either missing model. If an artifact cannot be obtained, the bake-off stays BLOCKED; there is no reduced pilot (Chat's ruling).
## E. Reachability note (MEASURED 2026-10-17)
huggingface.co (no response), dl.fbaipublicfiles.com (no response), download.pytorch.org (no response), github.com dinov2 and deep-person-reid repos (HTTP 403). The files must therefore be attached by the investigator.
