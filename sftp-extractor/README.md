# Introduction 
Extractor of CSVs files related from SFTP container to BigQuery tables.

# Getting Started

This project is built with 3.12.10.

1- Create Virtual environment
```
pip -m venv venv

./venv/Scripts/activate
```
2- Install requirements. With the virtual environment activated
```
pip install -r requirements.txt
```

# Build and Test

To deploy this function the pipeline must be configured with some environment variables:

- `PROJECTID`: Project identifier, should be one of `gc-t-plataformadeldato-ingesta` or `gc-p-plataformadeldato-ingesta` (default `gc-t-plataformadeldato-ingesta`)
- `PROJECTNUMBER`: Project number, should be one of `455912236365` or `933618847607` (default `455912236365`)
- `PROCESSNAME`: Process name identifier. Used to build BigQuery dataset name, connection credentials (secrets) name, gcs folder path:
  - BigQuery dataset: `bq_ing_sft_{{PROCESSNAME}}`
  - User name secret: `sftp-{{PROCESSNAME}}-user`
  - Password name secret: `sftp-{{PROCESSNAME}}-password`
  - GCS Folder preffix: `gs://{{bucket name}}/{{PROCESSNAME}/YYYY-MM-DD/{{file name}}`
- `SFTPHOST`: SFTP Host
- `SFTPPORT`: SFTP Port (default 2222)
- `SFTPFOLDER`: SFTP folder where files will be extracted. For root folder leave empty

## Debug
Open folder with VScode and launch *Plataforma del dato: SFTP extractor* debug config.

# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)