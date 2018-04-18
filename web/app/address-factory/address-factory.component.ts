import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  Validators
} from '@angular/forms';
import { HttpErrorAlertService } from '../shared/http-error-alert.service';
import { PublicConfigurationService } from '../shared/public.configuration.service';
import { PublicConfiguration } from '../shared/public-configuration.model';
import { RestService } from '../shared/rest.service';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/filter';

@Component({
  selector: 'app-address-factory',
  templateUrl: './address-factory.component.html',
  styleUrls: ['./address-factory.component.css']
})
export class AddressFactoryComponent implements OnInit {
  hasCoinAddress: boolean;

  @ViewChild('coinAddressInput') coinAddressInput: ElementRef;

  addressFactoryForm: FormGroup;
  publicConfiguration: PublicConfiguration;

  constructor(
    private fb: FormBuilder,
    private restService: RestService,
    private errorHandler: HttpErrorAlertService,
    publicConfigurationService: PublicConfigurationService
  ) {
    this.publicConfiguration = publicConfigurationService.configuration;
  }

  ngOnInit() {
    this.addressFactoryForm = this.fb.group({
      wavesAddress: ['', Validators.required],
      coinAddress: ''
    });
  }

  get wavesAddressControl(): AbstractControl {
    return this.addressFactoryForm.get('wavesAddress');
  }

  performRequest() {
    this.restService
      .getCoinAddress(this.addressFactoryForm.get('wavesAddress').value)
      .subscribe(
        res => {
          this.addressFactoryForm.get('coinAddress').patchValue(res);
          this.hasCoinAddress = true;
        },
        err => {
          if (err.status === 400) {
            this.addressFactoryForm.get('wavesAddress').setErrors({
              wavesAddressInvalid: true
            });
          } else {
            this.addressFactoryForm.get('wavesAddress').setErrors({
              serverError: true
            });
          }

          this.addressFactoryForm.get('coinAddress').reset();
        }
      );
  }

  onSubmit() {
    this.performRequest();
  }

  copyToClipboard() {
    this.coinAddressInput.nativeElement.select();
    console.log(document.execCommand('Copy'));
  }
}
