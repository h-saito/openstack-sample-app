# 概要
openstack-sample-appはOpenStackが提供するPythonのクライアントライブラリの代表的な利用方法を集めたサンプルプログラム群です。

## HP cloud向けAnsible OpenStackモジュール
### hp_nova_floating_ip
novaclientモジュールを利用したfloating_ipの生成・削除を行うモジュール

### hp_nova_floating_ip_associate
novaclientモジュールを利用したfloating_ipの割り当て・割り当て解除を行うモジュール

## OpenStackクライアント共通ライブラリ内の仮想リソース操作用クラス
### CinderClient()
仮想ブロックストレージを操作する

### GlanceClient()
GuestOSイメージを操作するサンプルプログラム

### KeystoneClient()
ユーザ・プロジェクト管理や認証操作を行うサンプルプログラム

### NeutronClient()
仮想ネットワークを操作するサンプルプログラム

### NovaClient()
仮想マシンを操作するサンプルプログラム

### SwiftClient()
オブジェクトストレージを操作するサンプルプログラム
