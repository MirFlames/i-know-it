#include "mydialog.h"
#include "ui_mydialog.h"
#include <QTextDocumentWriter>

MyDialog::MyDialog(QWidget *parent)
    : QDialog(parent)
    , ui(new Ui::MyDialog)
{
    setWindowTitle("Анкета");
    cBox->addItem("Elem 1");
    cBox->addItem("Elem 2");
    cBox->addItem("Elem 3");
    But->setText("Сохранить");
    Hlay->addWidget(sBox);
    Hlay->addWidget(tEdit);
    Hlay->addWidget(cBox);
    Hlay->addWidget(But);
    setLayout(Hlay);
    QObject::connect(But, SIGNAL(clicked()), this, SLOT(Wrf()));
}

MyDialog::~MyDialog()
{
    delete ui;
}

void MyDialog::Wrf()
{
    QString filename = QFileDialog::getSaveFileName(this, tr("Save text"), QString(), "Text file (*.txt)");
    if (filename.isEmpty())
        return;
    try
    {

        QSaveFile outfile(filename);
        outfile.open(QIODevice::WriteOnly);
        QTextStream ost(&outfile);
        ost << "Combo box: " << cBox->itemText(cBox->currentIndex()) << Qt::endl <<
        "Spin box: " << sBox->value() << Qt::endl <<
        "Text: " << Qt::endl << tEdit->toPlainText() << Qt::endl;
        outfile.commit();
    }
    catch (const std::exception &e)
    {
         QMessageBox::critical(this, "Error.", tr("Unable to write to the file %1: %2").arg(filename).arg(e.what()));
    }
}

