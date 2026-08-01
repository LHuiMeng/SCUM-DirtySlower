import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

SOURCE_DIR = Path("source")
BUILD_A = SOURCE_DIR / "version_a"
BUILD_B = SOURCE_DIR / "version_b"
REPAK = shutil.which("repak")
if not REPAK:
    for p in [r"C:\Users\Administrator\.cargo\bin\repak.exe",
              r"C:\Users\Administrator\.cargo\bin\repak"]:
        if Path(p).exists(): REPAK = p; break

UACLI_DLL = None
for p in [r"C:\Users\Administrator\hermes\UAssetCLI\UAssetCLI\UAssetCLI.dll",
          r"R:\Program Files\SCUMMod\UAssetCLI\UAssetCLI\UAssetCLI.dll"]:
    if Path(p).exists(): UACLI_DLL = p; break
DOTNET = shutil.which("dotnet") or r"C:\Program Files\dotnet\dotnet.exe"
ENGINE_VER = "VER_UE4_27"


def find_repak():
    if REPAK and Path(REPAK).exists():
        return REPAK
    raise FileNotFoundError("repak not found. Install from https://github.com/trumank/repak")


def build_version(version):
    """Build one version: tojson->edit->fromjson->repak"""
    src = BUILD_A if version == "A" else BUILD_B
    ua = src / "PhysicalSurfacesData.uasset"
    ue = src / "PhysicalSurfacesData.uexp"
    if not ua.exists() or not ue.exists():
        print(f"ERROR: source files not found in {src}")
        sys.exit(1)

    # Generate JSON
    json_tmp = src / "PhysicalSurfacesData.json"
    subprocess.run([DOTNET, UACLI_DLL, "tojson", str(ua), str(json_tmp), ENGINE_VER],
                   check=True, timeout=120)
    print(f"[{version}] tojson done")

    # Edit DirtinessFactor values (preserve current values from JSON)
    with open(json_tmp, "r", encoding="utf-8") as f:
        data = json.load(f)

    edits = 0
    for struct in data["Exports"][0]["Data"]:
        for prop in struct.get("Value", []):
            if prop.get("Name") == "DirtinessFactor":
                current_val = prop["Value"]
                target = {"A": 0.0, "B": 0.01}[version]
                if version == "A":
                    # Scale: keep relative proportions but very low
                    scale_map = {"Dirt": 0.20, "Mud": 0.20,
                                 "ForrestGroundContinental": 0.15,
                                 "ForrestGroundCoastal": 0.10,
                                 "Grass": 0.06, "Foliage": 0.06, "Flesh": 0.06,
                                 "GrassContinental": 0.06}
                    target = scale_map.get(struct["Name"], 0.02)
                prop["Value"] = target
                edits += 1

    with open(json_tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[{version}] edited {edits} DirtinessFactor values")

    # fromjson
    subprocess.run([DOTNET, UACLI_DLL, "fromjson", str(json_tmp), str(ua)],
                   check=True, timeout=120)
    print(f"[{version}] fromjson done")

    # repak
    pak_dir = str(src.parent.parent)  # goes up from source/version_X/ to WORK_DIR
    # Actually we need to repak from the source dir that has SCUM/ prefix
    # So the input dir is the parent of SCUM/
    input_dir = str(src / ".." / ".." / "..")  # source/version_a/SCUM/Content/... -> source/version_a/
    # Wait let me recalculate: src = source/version_a/SCUM/Content/ConZ_Files/Characters/Prisoner/Data/
    # The SCUM/ dir is at: source/version_a/SCUM/
    # So we need: source/version_a/ as input
    input_dir = str(src)
    while not (Path(input_dir) / "SCUM").exists():
        input_dir = str(Path(input_dir).parent)
        if input_dir == ".":
            print("ERROR: cannot find SCUM/ directory in source path")
            sys.exit(1)
    print(f"[{version}] input_dir for repak: {input_dir}")

    pak_name = f"SCUM-DirtySlower-{version}.pak"
    out = Path(pak_name)
    subprocess.run([find_repak(), "pack", input_dir, "--version", "V8B", "--compression", "Zlib", str(out)],
                   check=True, timeout=120)
    print(f"[{version}] pak created: {out} ({out.stat().st_size:,} bytes)")


def verify(version):
    pak = Path(f"SCUM-DirtySlower-{version}.pak")
    if not pak.exists():
        print(f"ERROR: {pak} not found")
        sys.exit(1)
    r = subprocess.run([find_repak(), "list", str(pak)], capture_output=True, text=True, timeout=30)
    files = [l.strip() for l in r.stdout.strip().split("\n") if l.strip()]
    print(f"[{version}] PAK contains {len(files)} files:")
    for f in files:
        print(f"  {f}")
    assert any("SCUM/Content" in f for f in files), f"PAK missing SCUM/ prefix!"
    print(f"[{version}] verification passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCUM-DirtySlower mod build tool")
    sp = parser.add_subparsers(dest="command")

    build_cmd = sp.add_parser("build", help="Build PAK from source")
    build_cmd.add_argument("--version", choices=["A", "B", "all"], default="all")

    verify_cmd = sp.add_parser("verify", help="Verify PAK content")
    verify_cmd.add_argument("--version", choices=["A", "B", "all"], default="all")

    args = parser.parse_args()
    if args.command == "build":
        versions = ["A", "B"] if args.version == "all" else [args.version]
        for v in versions:
            build_version(v)
    elif args.command == "verify":
        versions = ["A", "B"] if args.version == "all" else [args.version]
        for v in versions:
            verify(v)
    else:
        parser.print_help()
