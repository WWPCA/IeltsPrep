{pkgs}: {
  deps = [
    pkgs.zulu11
    pkgs.openjdk17
    pkgs.zip
    pkgs.awscli
    pkgs.unzip
    pkgs.aws-sam-cli
    pkgs.ffmpeg-full
    pkgs.postgresql
    pkgs.openssl
  ];
}
