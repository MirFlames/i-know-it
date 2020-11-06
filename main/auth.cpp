#include "auth.h"
#include "ui_auth.h"
#include <QIcon>

auth::auth(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::auth)
{
    ui->setupUi(this);
    setWindowIcon(QIcon(":/resources/icon.ico"));
}

auth::~auth()
{
    delete ui;
}
