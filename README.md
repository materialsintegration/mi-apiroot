APIサンドバックページ作成ツール

# 概要
本プロジェクトはWEBをGUIとして簡単にInventory-APIおよびGPDB-APIの動作を確認できるツールである。

# システム
* CentOS7.x
* python3.6
  + Flaskパッケージ
  + requestsパッケージ

# 準備
本プロジェクトを/var/lib以下などにクローンし、同梱のpage_contents.iniを対象サイトに合わせて編集する。

# 実行
本プロジェクトに同梱されているstart.shを実行すると、FlaskベースのWEBアプリケーションが実行される。
WEBページは、  
http://xxx.xxx.xxx.xxx:5000  
でアクセスする。

# WEBページについて

## GPDB

エンドポイントについてはGPDBマニュアルを参照する。

## Inventory-API

URLについてもInventory-API（参照系・更新系）のマニュアルを参照する。

API更新操作はまだ構築途中で動作しないので注意である。


